"""API速率限制器 - 令牌桶算法实现"""

import time
import asyncio
from typing import Dict
from loguru import logger


class RateLimiter:
    """API速率限制器"""

    def __init__(self, requests_per_second: float = 10, burst_size: int = 20):
        """
        初始化速率限制器

        Args:
            requests_per_second: 每秒允许的请求数
            burst_size: 令牌桶大小(允许的突发请求数)
        """
        self.rate = requests_per_second
        self.capacity = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self._lock = asyncio.Lock()

        logger.info(f"速率限制器已初始化: {requests_per_second} req/s, 突发={burst_size}")

    async def _refill_tokens(self):
        """补充令牌"""
        now = time.time()
        elapsed = now - self.last_update

        # 根据经过的时间补充令牌
        new_tokens = elapsed * self.rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_update = now

    async def acquire(self, tokens: int = 1) -> bool:
        """
        尝试获取令牌

        Args:
            tokens: 需要的令牌数

        Returns:
            是否成功获取令牌
        """
        async with self._lock:
            await self._refill_tokens()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    async def wait_for_token(self, tokens: int = 1):
        """
        等待直到获取到令牌

        Args:
            tokens: 需要的令牌数
        """
        while True:
            if await self.acquire(tokens):
                return

            # 计算需要等待的时间
            async with self._lock:
                await self._refill_tokens()
                if self.tokens >= tokens:
                    continue

                wait_time = (tokens - self.tokens) / self.rate
                logger.debug(f"速率限制: 等待 {wait_time:.2f}秒")

            await asyncio.sleep(min(wait_time, 1.0))

    async def get_remaining_tokens(self) -> float:
        """获取剩余令牌数"""
        async with self._lock:
            await self._refill_tokens()
            return self.tokens


class EndpointRateLimiter:
    """支持多个端点的速率限制器"""

    def __init__(self, default_rate: float = 10, default_burst: int = 20):
        """
        初始化多端点速率限制器

        Args:
            default_rate: 默认请求速率
            default_burst: 默认突发大小
        """
        self.default_rate = default_rate
        self.default_burst = default_burst
        self.limiters: Dict[str, RateLimiter] = {}

    def register_endpoint(self, endpoint: str, rate: float, burst: int):
        """
        注册端点的速率限制

        Args:
            endpoint: 端点名称
            rate: 请求速率
            burst: 突发大小
        """
        self.limiters[endpoint] = RateLimiter(rate, burst)
        logger.info(f"注册端点限制: {endpoint} - {rate} req/s")

    async def acquire(self, endpoint: str = 'default', tokens: int = 1) -> bool:
        """获取端点令牌"""
        if endpoint not in self.limiters:
            self.limiters[endpoint] = RateLimiter(
                self.default_rate,
                self.default_burst
            )

        return await self.limiters[endpoint].acquire(tokens)

    async def wait_for_token(self, endpoint: str = 'default', tokens: int = 1):
        """等待端点令牌"""
        if endpoint not in self.limiters:
            self.limiters[endpoint] = RateLimiter(
                self.default_rate,
                self.default_burst
            )

        await self.limiters[endpoint].wait_for_token(tokens)


# 全局速率限制器
_rate_limiter: EndpointRateLimiter = None


def get_rate_limiter() -> EndpointRateLimiter:
    """获取全局速率限制器"""
    global _rate_limiter
    if _rate_limiter is None:
        from ..utils.config import get_config
        config = get_config()
        _rate_limiter = EndpointRateLimiter(
            default_rate=config.api.requests_per_second,
            default_burst=config.api.burst_size
        )
    return _rate_limiter
