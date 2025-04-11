# core_logic/huffman_coder.py

import os
import struct
import pickle
from collections import Counter
from .data_structures import HuffmanNode, PriorityQueue

LENGTH_FORMAT = '>I'
PADDING_FORMAT = '>B'

# ... (_build_frequency_map, _build_huffman_tree, _generate_huffman_codes 不变) ...
# ... (_encode_data, _pad_encoded_string, _string_to_bytes 不变) ...

def _build_frequency_map(data: bytes) -> Counter:
    if not data: return Counter()
    return Counter(data)

def _build_huffman_tree(freq_map: Counter) -> HuffmanNode | None:
    if not freq_map: return None
    pq = PriorityQueue()
    for symbol, freq in freq_map.items():
        pq.insert(HuffmanNode(symbol=symbol, freq=freq))
    if pq.get_size() == 1:
        node = pq.extract_min()
        internal_node = HuffmanNode(freq=node.freq, left=node)
        return internal_node
    while pq.get_size() > 1:
        node1 = pq.extract_min()
        node2 = pq.extract_min()
        merged_freq = node1.freq + node2.freq
        internal_node = HuffmanNode(freq=merged_freq, left=node1, right=node2)
        pq.insert(internal_node)
    return pq.extract_min() if not pq.is_empty() else None

def _generate_huffman_codes(root: HuffmanNode | None) -> dict[int, str]:
    codes = {}
    if root is None: return codes
    def _traverse(node: HuffmanNode, current_code: str):
        if node is None: return
        if node.is_leaf():
            if node.symbol is not None : codes[node.symbol] = current_code if current_code else '0'
            return
        _traverse(node.left, current_code + '0')
        _traverse(node.right, current_code + '1')
    _traverse(root, "")
    if len(codes) == 0 and root.is_leaf() and root.symbol is not None: codes[root.symbol] = '0'
    elif len(codes) == 0 and not root.is_leaf() and root.left and root.left.is_leaf() and root.right is None:
        if root.left.symbol is not None: codes[root.left.symbol] = '0'
    return codes

def _encode_data(data: bytes, codes: dict[int, str]) -> str:
    encoded_str = "".join(codes[byte] for byte in data)
    return encoded_str

def _pad_encoded_string(encoded_str: str) -> tuple[str, int]:
    padding_amount = 8 - (len(encoded_str) % 8)
    if padding_amount == 8: padding_amount = 0
    padded_encoded_str = encoded_str + '0' * padding_amount
    return padded_encoded_str, padding_amount

def _string_to_bytes(padded_str: str) -> bytes:
    if len(padded_str) % 8 != 0: raise ValueError("填充后的字符串长度必须是8的倍数")
    byte_array = bytearray()
    for i in range(0, len(padded_str), 8):
        byte = padded_str[i:i+8]
        byte_array.append(int(byte, 2))
    return bytes(byte_array)


def compress(data: bytes, original_filename: str = "unknown") -> bytes | None:
    """执行哈夫曼压缩，并包含健壮的头部。"""
    # 1. 获取原始扩展名
    _, original_ext = os.path.splitext(original_filename)
    original_ext_bytes = original_ext.encode('utf-8')
    original_ext_len_bytes = struct.pack(LENGTH_FORMAT, len(original_ext_bytes))

    # 处理空数据：仍然需要头部信息
    if not data:
        freq_map = Counter()
        pickled_freq_map = pickle.dumps(freq_map)
        pickled_freq_map_len_bytes = struct.pack(LENGTH_FORMAT, len(pickled_freq_map))
        padding_amount = 0
        padding_info_byte = struct.pack(PADDING_FORMAT, padding_amount)
        encoded_data_bytes = b''
    else:
        # 2. 计算频率 & 序列化
        freq_map = _build_frequency_map(data)
        pickled_freq_map = pickle.dumps(freq_map)
        pickled_freq_map_len_bytes = struct.pack(LENGTH_FORMAT, len(pickled_freq_map))

        # 3. 构建树 & 生成编码
        huffman_tree_root = _build_huffman_tree(freq_map)
        if huffman_tree_root is None: return b'' # Logic error safeguard
        codes = _generate_huffman_codes(huffman_tree_root)
        if not codes and len(freq_map) > 0:
            if len(freq_map) == 1:
                 single_symbol = list(freq_map.keys())[0]
                 codes[single_symbol] = '0'
            else: raise RuntimeError("无法为非空频率表生成哈夫曼编码")

        # 4. 编码 & 填充 & 转字节
        encoded_string = _encode_data(data, codes)
        padded_encoded_string, padding_amount = _pad_encoded_string(encoded_string)
        encoded_data_bytes = _string_to_bytes(padded_encoded_string)
        padding_info_byte = struct.pack(PADDING_FORMAT, padding_amount)

    # 5. 组合新的头部和数据
    compressed_data = (
        original_ext_len_bytes +
        original_ext_bytes +
        pickled_freq_map_len_bytes +
        pickled_freq_map +
        padding_info_byte +
        encoded_data_bytes
    )
    return compressed_data

def _parse_header(data: bytes) -> tuple[str, Counter, int, int]: # Removed | None, let it raise error
    """解析新的健壮的文件头"""
    header_offset = 0
    struct_I_size = struct.calcsize(LENGTH_FORMAT)
    struct_B_size = struct.calcsize(PADDING_FORMAT)

    try:
        # 1. 解析扩展名长度
        if header_offset + struct_I_size > len(data): raise IndexError("数据不足以解析扩展名长度")
        ext_len = struct.unpack(LENGTH_FORMAT, data[header_offset : header_offset + struct_I_size])[0]
        header_offset += struct_I_size

        # 2. 解析扩展名
        if header_offset + ext_len > len(data): raise IndexError("数据不足以解析扩展名")
        original_ext = data[header_offset : header_offset + ext_len].decode('utf-8')
        header_offset += ext_len
        print(f">>> DEBUG (_parse_header): Parsed original_ext = '{original_ext}'") # <--- DEBUG PRINT

        # 3. 解析频率表长度
        if header_offset + struct_I_size > len(data): raise IndexError("数据不足以解析频率表长度")
        map_len = struct.unpack(LENGTH_FORMAT, data[header_offset : header_offset + struct_I_size])[0]
        header_offset += struct_I_size

        # 4. 解析频率表
        if header_offset + map_len > len(data): raise IndexError("数据不足以解析频率表")
        pickled_freq_map = data[header_offset : header_offset + map_len]
        freq_map_counter = pickle.loads(pickled_freq_map)
        if not isinstance(freq_map_counter, Counter): raise ValueError("Pickle data is not a Counter object.")
        header_offset += map_len
        print(f">>> DEBUG (_parse_header): Parsed freq_map_counter empty? {not freq_map_counter}") # <--- DEBUG PRINT


        # 5. 解析填充位数
        if header_offset + struct_B_size > len(data): raise IndexError("数据不足以解析填充位数")
        padding_amount = struct.unpack(PADDING_FORMAT, data[header_offset : header_offset + struct_B_size])[0]
        header_offset += struct_B_size
        print(f">>> DEBUG (_parse_header): Parsed padding_amount = {padding_amount}") # <--- DEBUG PRINT


        return original_ext, freq_map_counter, padding_amount, header_offset

    except (struct.error, IndexError, pickle.UnpicklingError, UnicodeDecodeError, ValueError) as e:
        raise ValueError(f"解析文件头失败: {e}") from e


def _decode_data(encoded_bytes: bytes, padding_amount: int, root: HuffmanNode | None) -> bytes: # Added | None for root
    """使用哈夫曼树解码字节数据。"""
    # ... (函数体与上一步相同，包括末尾的 current_node != root 检查) ...
    encoded_str = "".join(format(byte, '08b') for byte in encoded_bytes)
    if 0 <= padding_amount < 8:
        if padding_amount > 0:
            encoded_str = encoded_str[:-padding_amount]
    else:
        raise ValueError(f"无效的填充位数: {padding_amount}")

    if not encoded_str and root is None: return b'' # Empty data and empty tree
    if root is None and encoded_str : raise ValueError("解码错误：哈夫曼树为空，但编码数据存在")
    if root is None: return b'' # Empty tree implies empty data originally

    decoded_bytes = bytearray()
    if not encoded_str: # If padding removed all bits, original was likely empty
        if not _build_frequency_map(b''): # Check if the freq map was indeed empty
            return b''
        else: # Non-empty tree but no encoded bits after padding? Error.
             raise ValueError("解码错误：编码数据在移除填充后为空，但频率表非空")

    current_node = root
    # Handle single node tree cases first
    is_single_valid_leaf = root.is_leaf() and root.symbol is not None
    is_special_single_node = not root.is_leaf() and root.left and root.left.is_leaf() and root.right is None and root.left.symbol is not None

    if is_single_valid_leaf or is_special_single_node:
        leaf_symbol = root.symbol if is_single_valid_leaf else root.left.symbol
        # Expect encoded string to be all '0's
        if all(bit == '0' for bit in encoded_str):
             # As noted before, restoring exact length is hard without storing it.
             # We assume the number of '0' bits corresponds to original length for this specific case.
             num_symbols = len(encoded_str)
             if num_symbols > 0:
                decoded_bytes.extend([leaf_symbol] * num_symbols) # Replicate symbol
        elif encoded_str: # Contains non-'0' bits
            raise ValueError("解码错误：单符号树的编码包含无效位")
        # If encoded_str is empty here, decoded_bytes remains empty, which is correct for originally empty file
        return bytes(decoded_bytes)

    # Normal decoding loop
    for bit in encoded_str:
        if current_node is None: raise ValueError("解码错误：无效的树导航路径")
        if bit == '0': current_node = current_node.left
        elif bit == '1': current_node = current_node.right
        else: raise ValueError(f"解码错误：编码数据中包含无效位 '{bit}'")

        if current_node is None: raise ValueError("解码错误：无效的编码序列导致移动到 None")

        if current_node.is_leaf():
            if current_node.symbol is None: raise ValueError("解码错误：到达一个没有符号的叶子节点")
            decoded_bytes.append(current_node.symbol)
            current_node = root

    if current_node != root:
        raise ValueError("解码错误：编码数据在非符号边界处意外结束")

    return bytes(decoded_bytes)


def decompress(compressed_data: bytes) -> tuple[bytes, str]:
    """执行哈夫曼解压缩（使用新的头部格式）。"""
    if not compressed_data:
        return b'', ''

    print(">>> DEBUG (decompress): Starting decompression.") # <--- 新增

    try:
        # 1. 解析头部
        print(">>> DEBUG (decompress): Parsing header...") # <--- 新增
        parsed_header = _parse_header(compressed_data)
        # No need to check None here, _parse_header raises error now

        original_ext, freq_map_counter, padding_amount, header_end_offset = parsed_header
        print(f">>> DEBUG (decompress): Parsed original_ext = '{original_ext}', Freq map empty? {not freq_map_counter}, Padding: {padding_amount}, Header Offset: {header_end_offset}") # <--- 修改打印

        # 2. 获取编码数据
        encoded_data_bytes = compressed_data[header_end_offset:]
        print(f">>> DEBUG (decompress): Encoded data length: {len(encoded_data_bytes)}") # <--- 新增

        # 3. 重建哈夫曼树
        print(">>> DEBUG (decompress): Building Huffman tree...") # <--- 新增
        huffman_tree_root = _build_huffman_tree(freq_map_counter)

        # --- 空文件处理: 如果频率表为空，树就是 None ---
        if huffman_tree_root is None and not freq_map_counter:
             print(f">>> DEBUG (decompress): Empty file case detected. Returning ext: '{original_ext}'") # <--- 修改打印
             return b'', original_ext # 返回空数据和解析出的扩展名

        # 如果无法建树但频率表非空（理论上不应发生）
        elif huffman_tree_root is None and freq_map_counter:
             print(">>> DEBUG (decompress): Tree is None but freq map is not empty!") # <--- 新增
             raise ValueError("无法根据频率表重建哈夫曼树")

        print(f">>> DEBUG (decompress): Tree root built: {huffman_tree_root}") # <--- 新增
        # 4. 解码数据
        print(">>> DEBUG (decompress): Decoding data...") # <--- 新增
        decompressed_data = _decode_data(encoded_data_bytes, padding_amount, huffman_tree_root)
        print(">>> DEBUG (decompress): Decoding finished. Decompressed size:", len(decompressed_data)) # <--- 新增

        print(f">>> DEBUG (decompress): Returning data and ext: '{original_ext}'") # <--- 新增
        return decompressed_data, original_ext

    except (ValueError, struct.error, pickle.UnpicklingError, IndexError, EOFError, UnicodeDecodeError) as e: # Catch more parsing errors here
        print(f">>> DEBUG (decompress): Caught error: {type(e).__name__}: {e}") # <--- 新增
        raise ValueError(f"解压缩失败: {e}") from e


# ----- if __name__ == '__main__' 修改为只测试空文件，并处理导入问题 -----
if __name__ == '__main__':
    print("\n--- 直接运行 huffman_coder.py ---")

    # --- 临时解决直接运行时相对导入的问题 ---
    import sys
    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录 (core_logic 的上一级)
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    # 如果项目根目录不在 Python 搜索路径中，则添加
    if project_root not in sys.path:
        print(f">>> DEBUG: Adding project root to sys.path: {project_root}")
        sys.path.insert(0, project_root)
    # 现在可以尝试再次导入（或者依赖顶部的导入，如果 Python 版本支持）
    # 为确保，可以直接在这里重新导入一次，但通常调整 sys.path 就够了
    # from core_logic.huffman_coder import compress, decompress # 或者依赖顶部的导入即可
    # --- 导入问题处理结束 ---


    print("\n测试空数据:")
    empty_filename = "empty.txt"
    print(f"Compressing empty data with filename: {empty_filename}")
    compressed_empty = compress(b"", empty_filename) # 调用本文件的 compress
    print(f"压缩后的空数据 (头部): {compressed_empty}")
    print(f"压缩后长度: {len(compressed_empty)}")

    if compressed_empty:
        try:
            print(f"\nDecompressing the 'compressed' empty data...")
            # 调用本文件的 decompress
            decompressed_empty_data, decompressed_ext = decompress(compressed_empty)
            print(f"解压后数据: {decompressed_empty_data}")
            print(f"解压后长度: {len(decompressed_empty_data)}")
            print(f"恢复的原始扩展名: '{decompressed_ext}'") # <--- 重点观察这里的值
            print(f"验证: Data Empty? {decompressed_empty_data == b''}, Extension Correct? {decompressed_ext == '.txt'}")
        except ValueError as e:
            print(f"解压缩空数据时出错: {e}")
    else:
         print("压缩空数据返回了 None 或 b''，无法测试解压")