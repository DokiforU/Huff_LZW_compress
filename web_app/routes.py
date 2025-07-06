# huffman_webapp/web_app/routes.py

import os
import time
import uuid
import pickle
import struct # 确保导入
from flask import (Flask, request, jsonify, render_template,
                   send_from_directory, current_app, url_for, abort)
from werkzeug.utils import secure_filename
import tempfile
import zipfile
import traceback
from werkzeug.exceptions import RequestEntityTooLarge
import chardet

# 从 web_app 包导入 app 实例
from web_app import app

# --- 导入核心逻辑 ---
try:
    # 使用 'as' 重命名以区分
    from core_logic.huffman_coder import compress as huffman_compress, decompress as huffman_decompress
    # 新增：导入 LZW 函数
    from core_logic.lzw_coder import lzw_compress, lzw_decompress
    from core_logic.directory_handler import compress_directory, decompress_directory, is_valid_zip_file
except ImportError:
    # 处理直接运行或 PYTHONPATH 问题
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from core_logic.huffman_coder import compress as huffman_compress, decompress as huffman_decompress
    from core_logic.lzw_coder import lzw_compress, lzw_decompress # 确保这里也导入
    from core_logic.directory_handler import compress_directory, decompress_directory, is_valid_zip_file

# --- 配置常量 ---
DOWNLOAD_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'downloads'))
UPLOAD_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)

# --- 主页路由 ---
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='首页')

# --- 处理压缩/解压缩请求的路由 (集成 LZW 版本) ---
@app.route('/process', methods=['POST'])
def process_file():
    start_time = time.monotonic()
    print("[DEBUG] ====== /process 路由被调用 ======")
    try:
        # 1. 获取操作模式和算法
        mode = request.form.get('mode')
        algorithm = request.form.get('algorithm')
        is_directory = request.form.get('is_directory', 'false').lower() == 'true'
        print(f"[DEBUG] 参数: mode={mode}, algorithm={algorithm}, is_directory={is_directory}")
        print(f"[DEBUG] request.files keys: {list(request.files.keys())}")
        print(f"[DEBUG] request.form keys: {list(request.form.keys())}")

        if mode not in ['compress', 'decompress']:
            print(f"[ERROR] 非法 mode: {mode}")
            return jsonify({'status': 'error', 'error_type': 'FormatError', 'message': '无效的操作模式'}), 400
        if algorithm not in ['huffman', 'lzw']:
            print(f"[ERROR] 非法 algorithm: {algorithm}")
            return jsonify({'status': 'error', 'error_type': 'AlgorithmError', 'message': '无效的压缩算法'}), 400

        # 2. 获取输入数据
        input_data = None
        original_filename = "input_data"
        original_size = 0
        temp_dir = None

        if 'file' in request.files:
            file = request.files['file']
            print(f"[DEBUG] 上传文件对象: {file}, 文件名: {getattr(file, 'filename', None)}")
            if file and file.filename:
                if is_directory:
                    temp_dir = tempfile.mkdtemp()
                    file_path = os.path.join(temp_dir, secure_filename(file.filename))
                    file.save(file_path)
                    print(f"[DEBUG] 目录上传: 临时目录: {temp_dir}, 文件保存路径: {file_path}")
                    if file.filename.lower().endswith('.zip'):
                        print(f"[DEBUG] ZIP 文件解压: {file_path}")
                        with zipfile.ZipFile(file_path, 'r') as zipf:
                            zipf.extractall(temp_dir)
                        os.remove(file_path)
                    original_filename = os.path.basename(temp_dir)
                    original_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                     for dirpath, _, filenames in os.walk(temp_dir)
                                     for filename in filenames)
                    print(f"[DEBUG] 目录上传: original_filename={original_filename}, original_size={original_size}")
                else:
                    original_filename = secure_filename(file.filename)
                    input_data = file.read()
                    print(f"[DEBUG] 单文件上传, 文件名: {original_filename}, 读取字节数: {len(input_data) if input_data else 'None'}")
                    if not input_data or len(input_data) == 0:
                        print(f"[ERROR] 文件内容为空或读取失败: {original_filename}")
                        return jsonify({'status': 'error', 'error_type': 'FormatError', 'message': '文件内容为空或读取失败，请重新选择文件'}), 400
                    original_size = len(input_data)

        if input_data is None and not is_directory and 'text_input' in request.form:
            text = request.form.get('text_input', '').strip()
            print(f"[DEBUG] 文本输入: 长度={len(text)}")
            if text:
                input_data = text.encode('utf-8')
                original_filename = "pasted_text.txt"
                original_size = len(input_data)

        if input_data is None and not is_directory:
            print(f"[ERROR] 未提供文件或文本输入")
            return jsonify({'status': 'error', 'error_type': 'FormatError', 'message': '未提供文件或文本输入'}), 400

        # 新增：编码检测函数
        def detect_encoding(data: bytes):
            result = chardet.detect(data)
            encoding = result.get('encoding')
            confidence = result.get('confidence', 0)
            return encoding, confidence

        # 在单文件上传和处理逻辑中，压缩/解压前检测编码
        encoding_warning = None
        if input_data and original_filename.lower().endswith(('.txt', '.csv', '.log', '.md', '.json', '.xml', '.html', '.htm')):
            encoding, confidence = detect_encoding(input_data)
            if encoding and encoding.lower() != 'utf-8' and confidence > 0.7:
                encoding_warning = f"检测到文件编码为{encoding}，可能不是UTF-8，解压/查看时可能出现乱码。"

        # 3. 根据算法和模式调用核心逻辑
        output_data = None
        error_message = None
        final_size = 0
        original_ext = ''
        output_filename = None

        print(f"[DEBUG] 调用核心逻辑前: algorithm={algorithm}, mode={mode}, is_directory={is_directory}, original_filename={original_filename}, original_size={original_size}")

        try:
            if is_directory:
                if mode == 'compress':
                    if not temp_dir:
                        print(f"[ERROR] 临时目录创建失败")
                        raise ValueError("临时目录创建失败")
                    output_data, output_filename = compress_directory(temp_dir, algorithm)
                    final_size = len(output_data) if output_data is not None else 0
                    print(f"[DEBUG] 目录压缩完成: output_filename={output_filename}, final_size={final_size}")
                else:
                    if not input_data:
                        print(f"[ERROR] 未提供有效的压缩数据")
                        raise ValueError("未提供有效的压缩数据")
                    output_dir = os.path.join(DOWNLOAD_DIRECTORY, f"{original_filename}_decompressed")
                    decompress_directory(input_data, output_dir)
                    zip_path = f"{output_dir}.zip"
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, _, files in os.walk(output_dir):
                            for file in files:
                                file_path = os.path.join(root, file)
                                arcname = os.path.relpath(file_path, output_dir)
                                zipf.write(file_path, arcname)
                    with open(zip_path, 'rb') as f:
                        output_data = f.read()
                    final_size = len(output_data)
                    output_filename = os.path.basename(zip_path)
                    print(f"[DEBUG] 目录解压完成: output_filename={output_filename}, final_size={final_size}")
                    os.remove(zip_path)
                    import shutil
                    shutil.rmtree(output_dir)
            else:
                if not input_data:
                    print(f"[ERROR] 未提供有效的输入数据")
                    raise ValueError("未提供有效的输入数据")
                try:
                    # 只有解压模式下且上传zip才自动解包
                    if mode == 'decompress' and original_filename.lower().endswith('.zip'):
                        session_id = str(uuid.uuid4())
                        output_dir = os.path.join(DOWNLOAD_DIRECTORY, f"session_{session_id}")
                        decompress_directory(input_data, output_dir)
                        # 遍历所有文件，返回相对路径
                        file_list = []
                        for root, _, files in os.walk(output_dir):
                            for file in files:
                                abs_path = os.path.join(root, file)
                                rel_path = os.path.relpath(abs_path, DOWNLOAD_DIRECTORY)
                                file_list.append(rel_path)
                        response_data = {
                            'status': 'success',
                            'file_list': file_list,
                            'session_id': session_id
                        }
                        return jsonify(response_data)
                    else:
                        if algorithm == 'huffman':
                            if mode == 'compress':
                                output_data = huffman_compress(input_data, original_filename)
                                final_size = len(output_data) if output_data is not None else 0
                                print(f"[DEBUG] Huffman 压缩完成: final_size={final_size}")
                                # 设置输出文件名
                                base, _ = os.path.splitext(original_filename)
                                safe_base = secure_filename(base) if base else 'output'
                                output_filename = f"{safe_base}_compressed.huff"
                                print(f"[DEBUG] 设置输出文件名: {output_filename}")
                            else:
                                output_data, original_ext = huffman_decompress(input_data)
                                final_size = len(output_data) if output_data is not None else 0
                                print(f"[DEBUG] Huffman 解压完成: final_size={final_size}, original_ext={original_ext}")
                                # 设置输出文件名
                                base, _ = os.path.splitext(original_filename)
                                safe_base = secure_filename(base) if base else 'output'
                                output_filename = f"{safe_base}_decompressed.txt"
                                print(f"[DEBUG] 设置输出文件名: {output_filename}")
                        elif algorithm == 'lzw':
                            if mode == 'compress':
                                output_data = lzw_compress(input_data, original_filename)
                                final_size = len(output_data) if output_data is not None else 0
                                print(f"[DEBUG] LZW 压缩完成: final_size={final_size}")
                                # 设置输出文件名
                                base, _ = os.path.splitext(original_filename)
                                safe_base = secure_filename(base) if base else 'output'
                                output_filename = f"{safe_base}_compressed.lzw"
                                print(f"[DEBUG] 设置输出文件名: {output_filename}")
                            else:
                                output_data, original_ext = lzw_decompress(input_data)
                                final_size = len(output_data) if output_data is not None else 0
                                print(f"[DEBUG] LZW 解压完成: final_size={final_size}, original_ext={original_ext}")
                                # 设置输出文件名
                                base, _ = os.path.splitext(original_filename)
                                safe_base = secure_filename(base) if base else 'output'
                                output_filename = f"{safe_base}_decompressed.txt"
                                print(f"[DEBUG] 设置输出文件名: {output_filename}")
                except (MemoryError, RuntimeError, RecursionError) as e:
                    print(f"[ERROR] 压缩过程内存/递归/运行时异常: {type(e).__name__}: {e}")
                    traceback.print_exc()
                    return jsonify({'status': 'error', 'error_type': 'InternalError', 'message': '该文件内容不适合用Huffman/LZW压缩，建议直接传输原文件或用目录打包功能。'}), 400
        except RequestEntityTooLarge:
            print(f"[ERROR] 文件大小超过限制 (100MB)")
            return jsonify({'status': 'error', 'error_type': 'FileTooLarge', 'message': '文件大小超过限制 (100MB)，请压缩文件或使用目录打包功能'}), 413
        except Exception as e:
            print(f"[FATAL] 未捕获异常: {type(e).__name__}: {e}")
            traceback.print_exc()
            return jsonify({'status': 'error', 'error_type': 'InternalError', 'message': f'服务器内部错误，请稍后重试。 Error: {type(e).__name__}'}), 500

        if error_message:
            print(f"[ERROR] 核心逻辑返回错误: {error_message}")
            return jsonify({'status': 'error', 'error_type': 'InternalError', 'message': error_message}), 400
        if output_data is None:
            print(f"[ERROR] 核心处理逻辑未产生有效输出数据")
            return jsonify({'status': 'error', 'error_type': 'InternalError', 'message': '核心处理逻辑未产生有效输出数据'}), 500
        if output_filename is None:
            print(f"[ERROR] 输出文件名未正确设置")
            return jsonify({'status': 'error', 'error_type': 'InternalError', 'message': '输出文件名未正确设置'}), 500

        end_time = time.monotonic()
        duration = round(end_time - start_time, 3)
        print(f"[DEBUG] 处理完成: output_filename={output_filename}, duration={duration}s, original_size={original_size}, final_size={final_size}")

        if not is_directory:
            base, _ = os.path.splitext(original_filename)
            safe_base = secure_filename(base) if base else 'output'
            if mode == 'compress':
                ext = ".huff" if algorithm == 'huffman' else ".lzw"
                output_filename = f"{safe_base}_compressed{ext}"
            else:
                output_filename = f"{safe_base}_decompressed.txt"

        output_filepath = os.path.join(DOWNLOAD_DIRECTORY, output_filename)
        print(f"[DEBUG] 输出文件保存路径: {output_filepath}")
        try:
            with open(output_filepath, 'wb') as f_out:
                f_out.write(output_data)
        except IOError as e:
            print(f"[ERROR] 结果文件保存失败: {e}")
            return jsonify({'status': 'error', 'error_type': 'InternalError', 'message': f'无法保存结果文件: {e}'}), 500

        metrics = {
            'time': duration,
            'original_size': original_size,
            'final_size': final_size,
            'ratio': None
        }
        if mode == 'compress' and original_size > 0:
            ratio = (1 - (final_size / original_size)) * 100
            metrics['ratio'] = round(ratio, 2)
        elif mode == 'compress' and original_size == 0:
            metrics['ratio'] = 0.0

        response_data = {
            'status': 'success',
            'metrics': metrics,
            'output_filename': output_filename,
            'encoding_warning': encoding_warning
        }
        print(f"[DEBUG] 响应数据: {response_data}")
        return jsonify(response_data)

    except Exception as e:
        print(f"[FATAL] 外层异常: {type(e).__name__}: {e}")
        traceback.print_exc()
        return jsonify({'status': 'error', 'error_type': 'InternalError', 'message': f'服务器内部错误，请稍后重试。 Error: {type(e).__name__}'}), 500
    finally:
        if 'temp_dir' in locals() and temp_dir and os.path.exists(temp_dir):
            import shutil
            print(f"[DEBUG] 清理临时目录: {temp_dir}")
            shutil.rmtree(temp_dir)

# --- 文件下载路由 (保持不变) ---
@app.route('/download/<path:filename>')
def download_file(filename):
    safe_filename = secure_filename(filename)
    if not safe_filename or safe_filename != filename: abort(404)
    try:
        return send_from_directory(directory=DOWNLOAD_DIRECTORY, path=safe_filename, as_attachment=True)
    except FileNotFoundError: abort(404)
    except Exception as e: abort(500)

@app.route('/download_single')
def download_single():
    rel_path = request.args.get('path')
    if not rel_path:
        abort(400)
    abs_path = os.path.abspath(os.path.join(DOWNLOAD_DIRECTORY, rel_path))
    if not abs_path.startswith(DOWNLOAD_DIRECTORY):
        abort(403)
    if not os.path.isfile(abs_path):
        abort(404)
    return send_from_directory(DOWNLOAD_DIRECTORY, rel_path, as_attachment=True)

@app.route('/download_multi', methods=['POST'])
def download_multi():
    paths = request.json.get('paths')
    if not paths or not isinstance(paths, list):
        abort(400)
    import io, zipfile
    mem_zip = io.BytesIO()
    with zipfile.ZipFile(mem_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for rel_path in paths:
            abs_path = os.path.abspath(os.path.join(DOWNLOAD_DIRECTORY, rel_path))
            if not abs_path.startswith(DOWNLOAD_DIRECTORY) or not os.path.isfile(abs_path):
                continue
            arcname = os.path.basename(abs_path)
            zf.write(abs_path, arcname)
    mem_zip.seek(0)
    return send_from_directory(
        directory=os.path.dirname(mem_zip.name) if hasattr(mem_zip, 'name') else DOWNLOAD_DIRECTORY,
        path=os.path.basename(mem_zip.name) if hasattr(mem_zip, 'name') else 'selected_files.zip',
        as_attachment=True,
        mimetype='application/zip'
    )