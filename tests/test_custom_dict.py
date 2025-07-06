import unittest
import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core_logic.custom_dict import CustomDict

class TestCustomDict(unittest.TestCase):
    def setUp(self):
        """每个测试用例前创建新的字典实例"""
        self.dict = CustomDict()

    def test_initialization(self):
        """测试字典初始化"""
        self.assertEqual(len(self.dict), 0)
        self.assertEqual(self.dict.size, 256)  # 默认大小

    def test_basic_operations(self):
        """测试基本的字典操作"""
        # 测试设置和获取
        self.dict[1] = "one"
        self.assertEqual(self.dict[1], "one")
        
        # 测试键不存在
        with self.assertRaises(KeyError):
            _ = self.dict[2]
        
        # 测试get方法
        self.assertEqual(self.dict.get(1), "one")
        self.assertIsNone(self.dict.get(2))
        self.assertEqual(self.dict.get(2, "default"), "default")

    def test_bytes_keys(self):
        """测试字节序列作为键"""
        key1 = b"test"
        key2 = b"test2"
        self.dict[key1] = "value1"
        self.dict[key2] = "value2"
        
        self.assertEqual(self.dict[key1], "value1")
        self.assertEqual(self.dict[key2], "value2")
        self.assertIn(key1, self.dict)
        self.assertIn(key2, self.dict)

    def test_resize(self):
        """测试字典扩容"""
        # 添加足够多的元素触发扩容
        for i in range(200):  # 超过初始大小 * 负载因子
            self.dict[i] = f"value{i}"
        
        # 验证所有元素仍然可以访问
        for i in range(200):
            self.assertEqual(self.dict[i], f"value{i}")

    def test_items_keys_values(self):
        """测试items、keys和values方法"""
        test_data = {
            1: "one",
            2: "two",
            3: "three"
        }
        for k, v in test_data.items():
            self.dict[k] = v

        # 测试items
        items = self.dict.items()
        self.assertEqual(len(items), len(test_data))
        for k, v in items:
            self.assertEqual(v, test_data[k])

        # 测试keys
        keys = self.dict.keys()
        self.assertEqual(len(keys), len(test_data))
        for k in keys:
            self.assertIn(k, test_data)

        # 测试values
        values = self.dict.values()
        self.assertEqual(len(values), len(test_data))
        for v in values:
            self.assertIn(v, test_data.values())

    def test_collision_handling(self):
        """测试哈希冲突处理"""
        # 创建两个会产生相同哈希值的键
        self.dict[0] = "zero"
        self.dict[256] = "two_fifty_six"  # 假设哈希函数是 key % size
        
        self.assertEqual(self.dict[0], "zero")
        self.assertEqual(self.dict[256], "two_fifty_six")

    def test_lzw_specific(self):
        """测试LZW算法特定的用例"""
        # 测试初始化ASCII字符集
        dict_lzw = CustomDict(256)
        for i in range(256):
            dict_lzw[bytes([i])] = i
        
        # 验证所有ASCII字符都可以正确访问
        for i in range(256):
            self.assertEqual(dict_lzw[bytes([i])], i)

if __name__ == '__main__':
    unittest.main() 