# huffman_webapp/web_app/routes.py

import os
import time
import uuid
import pickle
import struct # 确保导入
from flask import (Flask, request, jsonify, render_template,
                   send_from_directory, current_app, url_for, abort)
from werkzeug.utils import secure_filename

# 从 web_app 包导入 app 实例
from web_app import app

# --- 导入核心逻辑 ---
try:
    # 使用 'as' 重命名以区分
    from core_logic.huffman_coder import compress as huffman_compress, decompress as huffman_decompress
    # 新增：导入 LZW 函数
    from core_logic.lzw_coder import lzw_compress, lzw_decompress
except ImportError:
    # 处理直接运行或 PYTHONPATH 问题
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from core_logic.huffman_coder import compress as huffman_compress, decompress as huffman_decompress
    from core_logic.lzw_coder import lzw_compress, lzw_decompress # 确保这里也导入

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
    try:
        # 1. 获取操作模式和算法
        mode = request.form.get('mode')
        algorithm = request.form.get('algorithm') # <--- 获取算法选择

        if mode not in ['compress', 'decompress']:
            return jsonify({'status': 'error', 'message': '无效的操作模式'}), 400
        if algorithm not in ['huffman', 'lzw']: # <--- 验证算法选择
             return jsonify({'status': 'error', 'message': '无效的压缩算法'}), 400

        # 2. 获取输入数据 (逻辑不变)
        input_data = None
        original_filename = "input_data"
        original_size = 0
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                original_filename = secure_filename(file.filename)
                input_data = file.read()
                original_size = len(input_data)
        if input_data is None and 'text_input' in request.form:
            text = request.form.get('text_input', '').strip()
            if text:
                input_data = text.encode('utf-8')
                original_filename = "pasted_text.txt"
                original_size = len(input_data)
        if input_data is None:
            return jsonify({'status': 'error', 'message': '未提供文件或文本输入'}), 400

        # 3. 根据算法和模式调用核心逻辑
        output_data = None
        error_message = None
        final_size = 0
        original_ext = '' # 用于解压时恢复

        print(f">>> DEBUG: Algorithm='{algorithm}', Mode='{mode}'") # 增加调试信息

        # --- 使用 if/elif 选择算法 ---
        if algorithm == 'huffman':
            print(">>> DEBUG: Calling Huffman logic...")
            if mode == 'compress':
                try:
                    output_data = huffman_compress(input_data, original_filename)
                    final_size = len(output_data)
                except Exception as e: error_message = f"Huffman 压缩过程中出错: {e}"
            else: # decompress
                try:
                    output_data, original_ext = huffman_decompress(input_data)
                    final_size = len(output_data)
                except ValueError as e: error_message = f"Huffman 解压缩失败: {e}"
                except Exception as e: error_message = f"Huffman 解压缩过程中发生意外错误: {e}"

        elif algorithm == 'lzw':
            print(">>> DEBUG: Calling LZW logic...")
            if mode == 'compress':
                try:
                    output_data = lzw_compress(input_data, original_filename)
                    final_size = len(output_data)
                except Exception as e: error_message = f"LZW 压缩过程中出错: {e}"
            else: # decompress
                try:
                    output_data, original_ext = lzw_decompress(input_data)
                    final_size = len(output_data)
                except ValueError as e: error_message = f"LZW 解压缩失败: {e}"
                except Exception as e: error_message = f"LZW 解压缩过程中发生意外错误: {e}"
        # --- 算法选择结束 ---

        # 检查核心逻辑错误
        if error_message:
             return jsonify({'status': 'error', 'message': error_message}), 400
        if output_data is None:
             return jsonify({'status': 'error', 'message': '核心处理逻辑未产生有效输出数据'}), 500

        # 4. 处理输出结果
        end_time = time.monotonic()
        duration = round(end_time - start_time, 3)

        # 生成输出文件名 (根据算法和模式)
        base, _ = os.path.splitext(original_filename)  # 获取上传文件的基本名
        safe_base = secure_filename(base) if base else 'output'

        if mode == 'compress':
            # 压缩文件名逻辑保持不变
            ext = ".huff" if algorithm == 'huffman' else ".lzw"
            output_filename = f"{safe_base}_compressed{ext}"
        else:  # decompress
            # !!! 修改点: 强制使用 _decompressed.txt 后缀 !!!
            # 不再需要 original_ext 或 safe_ext 变量来决定后缀
            output_filename = f"{safe_base}_decompressed.txt"

        output_filepath = os.path.join(DOWNLOAD_DIRECTORY, output_filename)

        # 写入文件 (逻辑不变)
        try:
            with open(output_filepath, 'wb') as f_out:
                f_out.write(output_data)
        except IOError as e:
             return jsonify({'status': 'error', 'message': f'无法保存结果文件: {e}'}), 500

        # 5. 准备成功响应 (逻辑基本不变)
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
            'output_filename': output_filename
        }
        return jsonify(response_data)

    except Exception as e:
        # (外部错误处理不变)
        # import traceback; traceback.print_exc() # 调试时打开
        return jsonify({'status': 'error', 'message': f'服务器内部错误，请稍后重试。 Error: {type(e).__name__}'}), 500


# --- 文件下载路由 (保持不变) ---
@app.route('/download/<path:filename>')
def download_file(filename):
    safe_filename = secure_filename(filename)
    if not safe_filename or safe_filename != filename: abort(404)
    try:
        return send_from_directory(directory=DOWNLOAD_DIRECTORY, path=safe_filename, as_attachment=True)
    except FileNotFoundError: abort(404)
    except Exception as e: abort(500)