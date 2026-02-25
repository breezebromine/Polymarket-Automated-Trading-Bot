"""内存缓存管理"""

from typing import Any, Optional, Dict
from datetime import datetime, timedelta
from collections import OrderedDict
import asyncio
from loguru import logger


class Cache:
    """简单的内存缓存实现"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        初始化缓存

        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认过期时间(秒)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存的值,如果不存在或已过期返回None
        """
        async with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # 检查是否过期
            if entry['expires_at'] and datetime.now() > entry['expires_at']:
                del self._cache[key]
                logger.debug(f"缓存过期: {key}")
                return None

            # 移到末尾(LRU)
            self._cache.move_to_end(key)
            return entry['value']

    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间(秒),None表示使用默认值
        """
        async with self._lock:
            ttl = ttl if ttl is not None else self.default_ttl
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None

            self._cache[key] = {
                'value': value,
                'expires_at': expires_at,
                'created_at': datetime.now()
            }

            # 移到末尾
            self._cache.move_to_end(key)

            # 检查是否超过最大容量
            if len(self._cache) > self.max_size:
                # 删除最旧的条目
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                logger.debug(f"缓存已满,删除最旧条目: {oldest_key}")

    async def delete(self, key: str):
        """删除缓存"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self):
        """清空所有缓存"""
        async with self._lock:
            self._cache.clear()
            logger.info("缓存已清空")

    async def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        return await self.get(key) is not None

    def size(self) -> int:
        """返回当前缓存数量"""
        return len(self._cache)

    async def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        async with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl
            }


# 全局缓存实例
_market_cache: Optional[Cache] = None
_price_cache: Optional[Cache] = None


def get_market_cache() -> Cache:
    """获取市场数据缓存"""
    global _market_cache
    if _market_cache is None:
        _market_cache = Cache(max_size=500, default_ttl=60)  # 1分钟
    return _market_cache


def get_price_cache() -> Cache:
    """获取价格数据缓存"""
    global _price_cache
    if _price_cache is None:
        _price_cache = Cache(max_size=2000, default_ttl=5)  # 5秒
    return _price_cache
