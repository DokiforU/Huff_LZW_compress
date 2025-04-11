import sys # 用于 sys.maxsize，可以代表无穷大或使用 None 检查

class HuffmanNode:
    """
    表示哈夫曼树中的一个节点。
    可以是叶子节点（包含一个符号）或内部节点。
    节点基于它们的频率进行比较。
    """
    def __init__(self, symbol=None, freq=0, left=None, right=None):
        """
        初始化一个哈夫曼节点。

        Args:
            symbol: 符号（字符/字节，用于叶子节点）。内部节点为 None。
            freq: 符号的频率或子节点频率之和。
            left: 左子节点。
            right: 右子节点。
        """
        self.symbol = symbol
        self.freq = freq
        self.left = left
        self.right = right

    def is_leaf(self):
        """检查节点是否为叶子节点。"""
        return self.left is None and self.right is None

    # 比较方法对于优先队列至关重要
    def __lt__(self, other):
        """根据频率比较节点（小于）。"""
        if not isinstance(other, HuffmanNode):
            # 不能与其他类型比较
            return NotImplemented
        return self.freq < other.freq

    def __eq__(self, other):
        """根据频率和符号检查相等性（可选，但良好实践）。"""
        if not isinstance(other, HuffmanNode):
            return False
        # 注意：比较内部节点可能仅依赖于频率或标识。
        # 为了稳定性/测试，可能需要比较结构，但频率是优先队列的关键。
        return self.freq == other.freq and self.symbol == other.symbol

    def __repr__(self):
        """提供节点的可读表示形式。"""
        symbol_repr = f"'{self.symbol}'" if self.symbol is not None else 'Internal'
        return f"Node({symbol_repr}, Freq:{self.freq})"


class PriorityQueue:
    """
    一个使用基于列表的二叉堆实现的最小优先队列。
    构建哈夫曼树时高效所需。
    **不使用** 内建的 `heapq` 模块。
    存储项目（预期为 HuffmanNode 实例）。
    """
    def __init__(self):
        """初始化一个空的最小堆。"""
        # 堆存储为一个列表。索引 0 是根节点。
        self._heap = []

    def get_size(self):
        """返回优先队列中的项目数量。"""
        return len(self._heap)

    def is_empty(self):
        """检查优先队列是否为空。"""
        return self.get_size() == 0

    def _parent(self, i):
        """返回索引 i 处节点的父节点索引。"""
        # 确保索引有效且不是根节点
        if i <= 0 or i >= self.get_size():
             # 或引发错误，-1 表示没有父节点/无效
            return -1
        return (i - 1) // 2

    def _left_child(self, i):
        """返回索引 i 处节点的左子节点索引。"""
        index = 2 * i + 1
        return index if index < self.get_size() else -1

    def _right_child(self, i):
        """返回索引 i 处节点的右子节点索引。"""
        index = 2 * i + 2
        return index if index < self.get_size() else -1

    def _swap(self, i, j):
        """交换堆中索引 i 和 j 处的元素。"""
        if 0 <= i < self.get_size() and 0 <= j < self.get_size():
            self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        # else: 处理错误或忽略？暂时忽略。

    def _sift_up(self, i):
        """
        将索引 i 处的元素向上移动以恢复堆属性。
        与父节点比较，如果当前节点更小则交换。
        """
        parent_idx = self._parent(i)
        # 当节点不是根节点且小于其父节点时
        while i > 0 and self._heap[i] < self._heap[parent_idx]:
            self._swap(i, parent_idx)
            i = parent_idx
            parent_idx = self._parent(i)

    def insert(self, item):
        """
        将一个项目插入优先队列并维护堆属性。
        Args:
            item: 要插入的项目（应是可比较的，例如 HuffmanNode）。
        """
        self._heap.append(item) # 添加到末尾
        self._sift_up(self.get_size() - 1) # 将其“冒泡”到正确位置

    def _sift_down(self, i):
        """
        将索引 i 处的元素向下移动以恢复堆属性。
        与子节点比较，如果当前节点更大则与较小的子节点交换。
        """
        min_index = i
        left = self._left_child(i)
        right = self._right_child(i)

        # 找出节点 i 及其子节点中最小元素的索引
        if left != -1 and self._heap[left] < self._heap[min_index]:
            min_index = left

        if right != -1 and self._heap[right] < self._heap[min_index]:
            min_index = right

        # 如果最小元素不是当前节点 i，则交换并继续向下调整
        if i != min_index:
            self._swap(i, min_index)
             # 从新位置递归地向下调整
            self._sift_down(min_index)

    def extract_min(self):
        """
        移除并返回具有最小优先级的项目（最小频率）。
        Returns:
            具有最小优先级的项目。
        Raises:
            IndexError: 如果优先队列为空。
        """
        if self.is_empty():
            raise IndexError("从空优先队列中提取最小值")

        min_item = self._heap[0] # 根节点是最小元素
        last_item = self._heap.pop() # 移除最后一个元素

        # 如果弹出后还有剩余项目
        if not self.is_empty():
            self._heap[0] = last_item # 将最后一个元素移到根位置
            self._sift_down(0) # 将其“下沉”到正确位置

        return min_item

    def peek_min(self):
        """ 返回具有最小优先级的项目但不移除它。 """
        if self.is_empty():
            raise IndexError("查看空优先队列的最小值")
        return self._heap[0]

# 示例用法（可选 - 用于在此文件内快速测试）
if __name__ == '__main__':
    # 创建一些节点
    node_a = HuffmanNode(symbol='a', freq=5)
    node_b = HuffmanNode(symbol='b', freq=9)
    node_c = HuffmanNode(symbol='c', freq=2)
    node_d = HuffmanNode(symbol='d', freq=6)

    # 创建一个优先队列
    pq = PriorityQueue()

    # 插入节点
    pq.insert(node_a)
    pq.insert(node_b)
    pq.insert(node_c)
    pq.insert(node_d)

    print(f"队列大小: {pq.get_size()}")
    print("提取最小元素:")
    while not pq.is_empty():
        node = pq.extract_min()
        print(f"提取出: {node}")

    print(f"提取后队列大小: {pq.get_size()}")