from typing import Any, List, Optional, Tuple, Iterator

class CustomDict:
    """
    自定义字典实现，使用哈希表作为底层数据结构。
    专门为 LZW 算法优化，支持字节序列作为键。
    """
    def __init__(self, initial_size=256):
        """
        初始化自定义字典。
        
        Args:
            initial_size: 初始大小，默认为256（对应ASCII字符集）
        """
        self.size = initial_size
        self.table: List[Optional[List[Tuple[Any, Any]]]] = [None] * self.size
        self.count = 0
        self.load_factor = 0.75  # 负载因子
        self.threshold = int(self.size * self.load_factor)

    def _hash(self, key):
        """
        计算键的哈希值。
        对于字节序列，使用简单的哈希函数。
        """
        if isinstance(key, bytes):
            # 对于字节序列，使用简单的哈希函数
            hash_value = 0
            for byte in key:
                hash_value = (hash_value * 31 + byte) % self.size
            return hash_value
        return hash(key) % self.size

    def _resize(self):
        """当负载因子超过阈值时，扩展哈希表"""
        old_table = self.table
        self.size *= 2
        self.table: List[Optional[List[Tuple[Any, Any]]]] = [None] * self.size
        self.threshold = int(self.size * self.load_factor)
        self.count = 0

        for item in old_table:
            if item is not None:
                for key, value in item:
                    self[key] = value

    def __setitem__(self, key: Any, value: Any) -> None:
        """设置键值对"""
        if self.count >= self.threshold:
            self._resize()

        index = self._hash(key)
        if self.table[index] is None:
            self.table[index] = []
        
        bucket = self.table[index]
        assert bucket is not None

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        bucket.append((key, value))
        self.count += 1

    def __getitem__(self, key: Any) -> Any:
        """获取键对应的值"""
        index = self._hash(key)
        bucket = self.table[index]
        if bucket is not None:
            for k, v in bucket:
                if k == key:
                    return v
        raise KeyError(f"Key not found: {key}")

    def __contains__(self, key):
        """检查键是否存在"""
        try:
            self[key]
            return True
        except KeyError:
            return False

    def get(self, key, default=None):
        """获取键对应的值，如果不存在返回默认值"""
        try:
            return self[key]
        except KeyError:
            return default

    def items(self):
        """返回所有键值对"""
        items = []
        for bucket in self.table:
            if bucket is not None:
                items.extend(bucket)
        return items

    def keys(self):
        """返回所有键"""
        return [k for k, _ in self.items()]

    def values(self):
        """返回所有值"""
        return [v for _, v in self.items()]

    def __len__(self):
        """返回字典中的键值对数量"""
        return self.count

    def __iter__(self) -> Iterator[Any]:
        for bucket in self.table:
            if bucket is not None:
                for k, _ in bucket:
                    yield k 