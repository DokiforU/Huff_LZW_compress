import os
import zipfile
import tempfile
from typing import List, Tuple, Optional
from .huffman_coder import compress as huffman_compress, decompress as huffman_decompress
from .lzw_coder import lzw_compress, lzw_decompress

def compress_directory(directory_path: str, algorithm: str = 'huffman') -> Tuple[bytes, str]:
    """
    压缩整个目录。
    
    Args:
        directory_path: 要压缩的目录路径
        algorithm: 使用的压缩算法 ('huffman' 或 'lzw')
        
    Returns:
        Tuple[bytes, str]: (压缩后的数据, 压缩后的文件名)
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"'{directory_path}' 不是一个有效的目录")
        
    # 创建临时ZIP文件
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        temp_zip_path = temp_zip.name
        
    # 创建ZIP文件
    with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 遍历目录
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                # 计算相对路径
                arcname = os.path.relpath(file_path, directory_path)
                
                # 读取文件内容
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # 使用选择的算法压缩文件内容
                if algorithm == 'huffman':
                    compressed_data = huffman_compress(file_data, arcname)
                else:  # lzw
                    compressed_data = lzw_compress(file_data, arcname)
                
                # 确保压缩数据不为None
                if compressed_data is None:
                    raise ValueError(f"压缩文件 '{arcname}' 失败")
                
                # 将压缩后的数据写入ZIP
                zipf.writestr(arcname, compressed_data)
    
    # 读取ZIP文件内容
    with open(temp_zip_path, 'rb') as f:
        zip_data = f.read()
    
    # 清理临时文件
    os.unlink(temp_zip_path)
    
    # 生成输出文件名
    dir_name = os.path.basename(directory_path)
    output_filename = f"{dir_name}_compressed_{algorithm}.zip"
    
    return zip_data, output_filename

def decompress_directory(compressed_data: bytes, output_dir: str) -> str:
    """
    解压缩目录。
    
    Args:
        compressed_data: 压缩后的数据
        output_dir: 解压缩的目标目录
        
    Returns:
        str: 解压缩后的目录路径
    """
    # 创建临时ZIP文件
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        temp_zip_path = temp_zip.name
        temp_zip.write(compressed_data)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 解压ZIP文件
        with zipfile.ZipFile(temp_zip_path, 'r') as zipf:
            # 遍历ZIP中的文件
            for file_info in zipf.infolist():
                try:
                    # 读取压缩数据
                    compressed_data = zipf.read(file_info)
                    
                    # 根据文件扩展名选择解压算法
                    filename = file_info.filename
                    if filename.endswith('.huff'):
                        decompressed_data, original_ext = huffman_decompress(compressed_data)
                        # 恢复原始文件名
                        base_name = os.path.splitext(filename)[0]
                        output_filename = base_name + original_ext
                    elif filename.endswith('.lzw'):
                        decompressed_data, original_ext = lzw_decompress(compressed_data)
                        # 恢复原始文件名
                        base_name = os.path.splitext(filename)[0]
                        output_filename = base_name + original_ext
                    else:
                        # 如果不是压缩文件，直接使用原始数据
                        decompressed_data = compressed_data
                        output_filename = filename
                    
                    # 确保输出路径存在
                    output_path = os.path.join(output_dir, output_filename)
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # 写入解压后的文件
                    with open(output_path, 'wb') as f:
                        f.write(decompressed_data)
                        
                except Exception as e:
                    print(f"处理文件 {file_info.filename} 时出错: {str(e)}")
                    continue
                    
    except zipfile.BadZipFile:
        raise ValueError("无效的ZIP文件格式")
    except Exception as e:
        raise ValueError(f"解压缩ZIP文件时出错: {str(e)}")
    finally:
        # 清理临时文件
        try:
            os.unlink(temp_zip_path)
        except:
            pass
    
    return output_dir

def is_valid_zip_file(file_path: str) -> bool:
    """
    检查文件是否为有效的ZIP文件。
    
    Args:
        file_path: 要检查的文件路径
        
    Returns:
        bool: 如果是有效的ZIP文件返回True，否则返回False
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zipf:
            # 尝试读取文件列表
            zipf.infolist()
            return True
    except:
        return False 