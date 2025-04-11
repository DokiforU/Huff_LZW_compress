# core_logic/lzw_coder.py

import struct
import os

# --- 常量定义 ---
# LZW 通常使用 12 位编码比较常见且有效，最大编码值为 4095
# 也可以使用 16 位 (65535)，打包/解包更简单，但可能效率稍低
CODE_WIDTH = 12  # 选择编码位宽 (例如 12 位)
MAX_CODES = 1 << CODE_WIDTH  # 2^CODE_WIDTH，例如 4096
INITIAL_DICT_SIZE = 256

# 用于打包/解包头部长度信息的格式 (4字节无符号整数，大端)
LENGTH_FORMAT = '>I'
# 用于打包/解包编码的格式 (选择 16 位 '>H' 更简单，但会浪费空间如果用 12 位编码)
# 如果使用 12 位，打包/解包会复杂很多，需要位操作。
# 为了简化，我们暂时牺牲一点效率，使用 16 位来存储编码。
# 注意：这意味着 MAX_CODES 实际上可以是 65536，但我们仍按 CODE_WIDTH=12 来限制字典增长
# 或者，我们可以坚持使用 CODE_WIDTH=12，并实现复杂的位打包。
# --> 折衷方案：内部逻辑按 CODE_WIDTH=12 (MAX_CODES=4096) 限制字典增长，
# --> 但输出时仍按 16 位打包，简化 I/O 操作。
PACK_FORMAT = '>H' # 使用 16 位 (unsigned short) 打包


# --- LZW 压缩 ---
def lzw_compress(data: bytes, original_filename: str = "unknown") -> bytes:
    """
    使用 LZW 算法压缩字节数据。

    Args:
        data: 原始字节数据。
        original_filename: 原始文件名，用于提取扩展名存入头部。

    Returns:
        压缩后的字节数据 (包含头部)。空输入返回只包含头部的空数据。
        Header Format:
        [4 bytes: length of original_ext_bytes (L_ext)]
        [L_ext bytes: original_ext_bytes (encoded in utf-8)]
        [N bytes: Packed Code Sequence (16 bits/code)]
    """
    # 1. 初始化字典 (使用 Python 内建 dict 作为核心数据结构)
    # 这是 LZW 算法的核心部分，我们将手动实现其使用逻辑
    encoding_dict = {bytes([i]): i for i in range(INITIAL_DICT_SIZE)}
    next_code = INITIAL_DICT_SIZE

    # 2. 准备头部信息 - 原始扩展名
    _, original_ext = os.path.splitext(original_filename)
    original_ext_bytes = original_ext.encode('utf-8')
    original_ext_len_bytes = struct.pack(LENGTH_FORMAT, len(original_ext_bytes))

    # 3. 压缩主循环
    output_codes = []
    current_sequence = b""
    for byte_val in data:
        current_byte = bytes([byte_val])
        new_sequence = current_sequence + current_byte
        if new_sequence in encoding_dict:
            current_sequence = new_sequence
        else:
            output_codes.append(encoding_dict[current_sequence])
            # 检查字典是否已满 (根据 CODE_WIDTH)
            if next_code < MAX_CODES:
                encoding_dict[new_sequence] = next_code
                next_code += 1
            current_sequence = current_byte

    # 输出最后一个序列的编码
    if current_sequence:
        output_codes.append(encoding_dict[current_sequence])

    # 4. 打包编码序列为字节流 (使用 16 位)
    packed_codes = b"".join(struct.pack(PACK_FORMAT, code) for code in output_codes)

    # 5. 组合头部和压缩数据
    compressed_data = original_ext_len_bytes + original_ext_bytes + packed_codes
    return compressed_data


# --- LZW 解压缩 ---
def lzw_decompress(compressed_data: bytes) -> tuple[bytes, str]:
    """
    使用 LZW 算法解压缩数据。

    Args:
        compressed_data: 包含头部的压缩字节数据。

    Returns:
        一个元组 (decompressed_data: bytes, original_extension: str)。
        如果输入无效或为空，引发 ValueError 或返回 (b'', '')。

    Raises:
        ValueError: 如果数据损坏或格式不正确。
    """
    if not compressed_data:
        return b'', ''

    header_offset = 0
    ext_len_size = struct.calcsize(LENGTH_FORMAT) # 4
    code_size = struct.calcsize(PACK_FORMAT)     # 2 (因为用了'>H')

    try:
        # 1. 解析头部 - 原始扩展名
        if header_offset + ext_len_size > len(compressed_data):
            raise ValueError("数据过短，无法解析扩展名长度")
        ext_len = struct.unpack(LENGTH_FORMAT, compressed_data[header_offset:header_offset+ext_len_size])[0]
        header_offset += ext_len_size

        if header_offset + ext_len > len(compressed_data):
             raise ValueError("数据过短，无法解析扩展名")
        original_ext = compressed_data[header_offset:header_offset+ext_len].decode('utf-8')
        header_offset += ext_len

        # 编码数据部分
        packed_codes_data = compressed_data[header_offset:]
        if len(packed_codes_data) % code_size != 0:
             raise ValueError("编码数据长度不是预期字节数的整数倍")

        # 2. 初始化字典 (使用 Python 内建 dict)
        decoding_dict = {i: bytes([i]) for i in range(INITIAL_DICT_SIZE)}
        next_code = INITIAL_DICT_SIZE

        # 3. 解压缩主循环
        output_sequences = []

        # 处理第一个编码
        if not packed_codes_data: # 如果只有头部（原始文件为空）
             return b'', original_ext

        previous_code = struct.unpack(PACK_FORMAT, packed_codes_data[0:code_size])[0]
        if previous_code >= INITIAL_DICT_SIZE: # 第一个编码必须是基础字符
            raise ValueError(f"无效的起始编码: {previous_code}")
        previous_sequence = decoding_dict[previous_code]
        output_sequences.append(previous_sequence)

        # 处理剩余编码
        for i in range(code_size, len(packed_codes_data), code_size):
            current_code = struct.unpack(PACK_FORMAT, packed_codes_data[i:i+code_size])[0]

            current_sequence = b''
            # KwKwK 情况 或 字典中存在
            if current_code == next_code: # KwKwK
                if not previous_sequence: # 防止 previous_sequence 为空
                    raise ValueError("解码错误：KwKwK 情况发生在无效的前序序列之后")
                current_sequence = previous_sequence + previous_sequence[:1]
            elif current_code in decoding_dict:
                current_sequence = decoding_dict[current_code]
            else: # 编码超出范围或丢失
                raise ValueError(f"解码错误：遇到未知的编码 {current_code}")

            output_sequences.append(current_sequence)

            # 添加新条目到字典 (如果未满)
            if next_code < MAX_CODES:
                 if not previous_sequence or not current_sequence: # 安全检查
                     raise ValueError("解码错误：尝试向字典添加条目时序列无效")
                 decoding_dict[next_code] = previous_sequence + current_sequence[:1]
                 next_code += 1

            # 更新前一个序列
            previous_sequence = current_sequence
            # previous_code = current_code # 实际上 KwKwK 判断用了 next_code，不需要 previous_code

        # 4. 合并结果
        decompressed_data = b"".join(output_sequences)
        return decompressed_data, original_ext

    except (struct.error, IndexError, UnicodeDecodeError, ValueError) as e:
        raise ValueError(f"解压缩失败: {e}") from e
    except Exception as e: # 捕获其他意外错误
        raise ValueError(f"解压缩时发生意外错误: {e}") from e


# ----- 简单的本地测试 -----
if __name__ == '__main__':
    test_filename = "example_lzw.txt"
    test_data = b"TOBEORNOTTOBEORTOBEORNOT" * 5
    print(f"原始数据 ({test_filename}): {test_data}")
    print(f"原始长度: {len(test_data)} bytes")

    compressed = lzw_compress(test_data, test_filename)
    print(f"压缩后数据 (前100字节): {compressed[:100]}...")
    print(f"压缩后长度: {len(compressed)} bytes")

    try:
        decompressed, original_ext = lzw_decompress(compressed)
        print(f"解压后数据: {decompressed}")
        print(f"解压后长度: {len(decompressed)} bytes")
        print(f"恢复的原始扩展名: {original_ext}")

        # 验证
        if test_data == decompressed and original_ext == ".txt":
            print("LZW 成功: 解压缩后的数据和扩展名与原始匹配！")
        else:
            print("！！！LZW 失败: 解压缩后的数据或扩展名与原始不匹配！！！")
            if test_data != decompressed: print("    - 数据不匹配")
            if original_ext != ".txt": print(f"    - 扩展名不匹配 (expected .txt, got {original_ext})")

    except ValueError as e:
        print(f"LZW 解压缩时出错: {e}")

    print("\n测试空数据:")
    compressed_empty = lzw_compress(b"", "empty.dat")
    print(f"压缩空数据: {compressed_empty}")
    decompressed_empty, ext_empty = lzw_decompress(compressed_empty)
    print(f"解压空数据: {decompressed_empty}, 原始扩展名: {ext_empty}")
    print(f"空数据验证成功: {b'' == decompressed_empty and ext_empty == '.dat'}")