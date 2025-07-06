# tests/test_huffman_coder.py

import unittest
import os
import sys
import random
import pickle # 仅用于测试可能无效的 pickle 数据
from typing import Optional

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core_logic.huffman_coder import compress, decompress

class TestHuffmanCoder(unittest.TestCase):
    """测试 huffman_coder.py 中的 compress 和 decompress 函数"""

    def _assert_reversible(self, data: bytes, filename: str = "test.file", msg: str = ""):  # 添加 filename 参数
        """辅助方法：断言 Huffman 压缩解压可逆，并检查扩展名"""
        if not msg:
            msg_prefix = f"Huffman可逆性失败 ({filename}): "
            msg_data = data[:50].decode('latin-1', errors='replace') + ('...' if len(data) > 50 else '')
            msg = msg_prefix + msg_data

        # 压缩时需要传入文件名
        compressed_data = compress(data, filename)
        self.assertIsNotNone(compressed_data, f"Huffman压缩不应返回 None 对于: {msg}")
        # 确保压缩数据是bytes类型
        self.assertIsInstance(compressed_data, bytes, f"压缩数据必须是bytes类型 对于: {msg}")

        # 解压缩
        try:
            # 由于我们已经确保了compressed_data是bytes类型，这里不会有类型错误
            decompressed_data, original_ext = decompress(compressed_data)  # type: ignore
            _, expected_ext = os.path.splitext(filename)  # 从传入的文件名获取预期扩展名

            # 比较数据部分
            self.assertEqual(data, decompressed_data, msg)
            # 比较扩展名
            self.assertEqual(expected_ext, original_ext, f"Huffman扩展名恢复失败 ({filename})")

        except ValueError as e:
            # 对有效数据解压时，不应出现 ValueError
            self.fail(f"为有效 Huffman 压缩数据解压时引发 ValueError: {e} 对于: {msg}")
        except Exception as e:
            self.fail(f"为有效 Huffman 压缩数据解压时引发意外异常: {type(e).__name__}: {e} 对于: {msg}")

    # 例如:
    def test_empty_data(self):
        self._assert_reversible(b"", "empty.txt", "空数据测试")

    def test_single_byte_data(self):
        self._assert_reversible(b"a", "single.bin", "单字节数据测试")

    def test_single_unique_byte_data(self):
        self._assert_reversible(b"aaaaabbbbb", "repeats.dat", "仅含'a' 'b'的数据测试")
        self._assert_reversible(b"aaaaa", "only_a.txt", "仅含单一重复字节 'a' 的数据测试")

    # ... (为其他调用 _assert_reversible 的测试方法都加上 filename 参数) ...
    def test_simple_text_data(self):
        self._assert_reversible(b"hello world", "hello.txt", "简单文本'hello world'测试")
        self._assert_reversible(b"beep boop beer! Go Bulldogs! Testing 123...", "complex.txt", "较复杂文本测试")

    def test_data_with_all_bytes(self):
        data = bytes(range(256)) * 3
        data_list = list(data)
        random.shuffle(data_list)
        data = bytes(data_list)
        self._assert_reversible(data, "all_bytes.bin", "包含所有字节值数据测试")

    def test_longer_text_data(self):
        data = (b"...") * 5  # 省略长文本
        self._assert_reversible(data, "long.log", "较长文本数据测试")

    def test_decompress_invalid_data(self):
        """测试解压缩无效或损坏的数据（应引发 ValueError）"""
        # 1. 随机字节 (不太可能形成有效的头部)
        invalid_data_random = bytes([random.randint(0, 255) for _ in range(50)])
        with self.assertRaises(ValueError, msg="解压缩随机字节应引发 ValueError"):
            decompress(invalid_data_random)

        # 2. 太短的数据 (无法包含有效的头部和填充信息)
        invalid_data_short = b"abc"
        with self.assertRaises(ValueError, msg="解压缩过短数据应引发 ValueError"):
            decompress(invalid_data_short)

        # 3. 有效压缩数据但被截断 (可能破坏 pickle 或数据部分)
        valid_data = b"some valid text"
        compressed_valid = compress(valid_data)
        if compressed_valid and len(compressed_valid) > 5:
             truncated_data = compressed_valid[:-5] # 截断尾部
             with self.assertRaises(ValueError, msg="解压缩截断数据应引发 ValueError"):
                 decompress(truncated_data)

        # 4. 模拟损坏的 pickle 头部 (例如，非 pickle 数据 + 一个字节的填充信息)
        bad_header_data = b"not pickle data" + b'\x03' # 假设填充 3 位
        with self.assertRaises(ValueError, msg="解压缩损坏头部应引发 ValueError"):
             decompress(bad_header_data)

        # 5. 模拟 pickle 数据类型错误 (非 Counter)
        not_a_counter = {"a": 1, "b": 2} # 是字典但不是 Counter
        bad_pickle_type_header = pickle.dumps(not_a_counter) + b'\x01'
        with self.assertRaises(ValueError, msg="解压缩头部类型错误应引发 ValueError"):
            decompress(bad_pickle_type_header)


    # 可选：更精确的压缩结果验证（比较脆弱）
    # def test_specific_compression_output(self):
    #     """测试特定输入的精确压缩输出"""
    #     data = b"aaab"
    #     # 手动计算预期结果 (非常依赖实现细节，如 pickle 协议版本)
    #     # freq = {'a': 3, 'b': 1} -> Counter({97: 3, 98: 1})
    #     # 假设 pickle 结果是 X, padding 是 Y, encoded data 是 Z
    #     # expected_compressed = X + Y_byte + Z_bytes
    #     # self.assertEqual(compress(data), expected_compressed)
    #     pass # 通常不推荐，除非有非常稳定的格式和需求


if __name__ == '__main__':
    unittest.main()