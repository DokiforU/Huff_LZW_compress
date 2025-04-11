import unittest
# 确保 core_logic 在 Python 路径上，对于 PyCharm 通常自动处理
# 如果在终端运行 unittest 发现模块找不到，可能需要设置 PYTHONPATH 或使用 python -m unittest discover
from core_logic.data_structures import HuffmanNode, PriorityQueue

class TestHuffmanNode(unittest.TestCase):
    """测试 HuffmanNode 类"""

    def test_node_creation(self):
        """测试节点的基本属性创建"""
        node = HuffmanNode(symbol='a', freq=10)
        self.assertEqual(node.symbol, 'a')
        self.assertEqual(node.freq, 10)
        self.assertIsNone(node.left)
        self.assertIsNone(node.right)
        self.assertTrue(node.is_leaf())

        internal_node = HuffmanNode(freq=15, left=node, right=HuffmanNode('b', 5))
        self.assertIsNone(internal_node.symbol)
        self.assertEqual(internal_node.freq, 15)
        self.assertIsNotNone(internal_node.left)
        self.assertIsNotNone(internal_node.right)
        self.assertFalse(internal_node.is_leaf())

    def test_node_comparison(self):
        """测试节点基于频率的比较 (<)"""
        node_low = HuffmanNode(symbol='c', freq=5)
        node_high = HuffmanNode(symbol='d', freq=20)
        node_equal = HuffmanNode(symbol='e', freq=5)

        self.assertTrue(node_low < node_high)
        self.assertLess(node_low, node_high) # 等同于 assertTrue(node_low < node_high)

        self.assertFalse(node_high < node_low)
        self.assertFalse(node_low < node_equal) # 频率相等，不满足 <

    def test_node_equality(self):
        """测试节点的相等性 (==)"""
        node1 = HuffmanNode('a', 10)
        node2 = HuffmanNode('a', 10)
        node3 = HuffmanNode('b', 10)
        node4 = HuffmanNode('a', 15)

        self.assertEqual(node1, node2) # 符号和频率都相同
        self.assertNotEqual(node1, node3) # 符号不同
        self.assertNotEqual(node1, node4) # 频率不同

        # 内部节点比较（我们的实现主要依赖频率比较，这里仅作示例）
        internal1 = HuffmanNode(freq=10, left=node1)
        internal2 = HuffmanNode(freq=10, left=node1) # 结构相同但对象不同
        internal3 = HuffmanNode(freq=15)
        # 注意：默认的 __eq__ 不会递归比较子节点，除非你特别实现
        # 我们的 __eq__ 实现目前只比较 symbol 和 freq
        self.assertEqual(internal1.freq, internal2.freq) # 频率相同
        self.assertNotEqual(internal1.freq, internal3.freq) # 频率不同

class TestPriorityQueue(unittest.TestCase):
    """测试手动实现的 PriorityQueue 类"""

    def setUp(self):
        """在每个测试方法运行前设置"""
        self.pq = PriorityQueue()
        # 创建一些测试节点
        self.node_c = HuffmanNode(symbol='c', freq=2)
        self.node_a = HuffmanNode(symbol='a', freq=5)
        self.node_d = HuffmanNode(symbol='d', freq=6)
        self.node_b = HuffmanNode(symbol='b', freq=9)
        self.nodes = [self.node_c, self.node_a, self.node_d, self.node_b] # 按频率排序：c, a, d, b

    def test_initialization(self):
        """测试优先队列初始化状态"""
        self.assertTrue(self.pq.is_empty())
        self.assertEqual(self.pq.get_size(), 0)

    def test_insert_single(self):
        """测试插入单个元素"""
        self.pq.insert(self.node_a)
        self.assertFalse(self.pq.is_empty())
        self.assertEqual(self.pq.get_size(), 1)
        # 可以选择性地检查内部 _heap 状态，但更推荐通过 extract_min 验证
        # self.assertEqual(self.pq._heap[0], self.node_a)

    def test_insert_multiple_and_size(self):
        """测试插入多个元素和队列大小"""
        self.pq.insert(self.node_a)
        self.pq.insert(self.node_c) # 频率最低
        self.pq.insert(self.node_b)
        self.assertEqual(self.pq.get_size(), 3)
        # 检查最小值是否是频率最低的 'c'
        # 注意：peek_min 会暴露内部实现，最好通过 extract_min 验证
        # 如果你实现了 peek_min: self.assertEqual(self.pq.peek_min(), self.node_c)

    def test_extract_min_empty(self):
        """测试从空队列提取最小值（应抛出异常）"""
        with self.assertRaises(IndexError):
            self.pq.extract_min()

    def test_extract_min_single(self):
        """测试插入一个元素后提取"""
        self.pq.insert(self.node_a)
        extracted = self.pq.extract_min()
        self.assertEqual(extracted, self.node_a)
        self.assertTrue(self.pq.is_empty())
        self.assertEqual(self.pq.get_size(), 0)

    def test_extract_min_order(self):
        """测试插入多个元素后按频率顺序提取"""
        # 按任意顺序插入
        self.pq.insert(self.node_a) # freq 5
        self.pq.insert(self.node_b) # freq 9
        self.pq.insert(self.node_c) # freq 2
        self.pq.insert(self.node_d) # freq 6

        self.assertEqual(self.pq.get_size(), 4)

        # 按频率升序提取
        extracted_nodes = []
        while not self.pq.is_empty():
            extracted_nodes.append(self.pq.extract_min())

        # 期望的顺序是 c, a, d, b (按频率 2, 5, 6, 9)
        expected_order = [self.node_c, self.node_a, self.node_d, self.node_b]
        self.assertEqual(extracted_nodes, expected_order)
        self.assertTrue(self.pq.is_empty())

    def test_mixed_operations(self):
        """测试插入和提取混合操作"""
        self.pq.insert(self.node_a) # 5
        self.pq.insert(self.node_c) # 2
        self.assertEqual(self.pq.get_size(), 2)

        min1 = self.pq.extract_min() # 提取 c (2)
        self.assertEqual(min1, self.node_c)
        self.assertEqual(self.pq.get_size(), 1)

        self.pq.insert(self.node_d) # 插入 d (6)
        self.pq.insert(self.node_b) # 插入 b (9)
        self.assertEqual(self.pq.get_size(), 3) # 现在有 a(5), d(6), b(9)

        min2 = self.pq.extract_min() # 提取 a (5)
        self.assertEqual(min2, self.node_a)
        self.assertEqual(self.pq.get_size(), 2)

        min3 = self.pq.extract_min() # 提取 d (6)
        self.assertEqual(min3, self.node_d)
        self.assertEqual(self.pq.get_size(), 1)

        min4 = self.pq.extract_min() # 提取 b (9)
        self.assertEqual(min4, self.node_b)
        self.assertTrue(self.pq.is_empty())

    # 可以添加更多测试用例，例如测试具有相同频率的节点

if __name__ == '__main__':
    unittest.main()