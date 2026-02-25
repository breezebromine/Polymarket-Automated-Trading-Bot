"""市场数据采集器"""

import asyncio
from typing import List, Dict
from loguru import logger

from ..api.polymarket_client import get_client
from .cache import get_market_cache, get_price_cache
from .database import get_session
from .models import Market, Price


class DataCollector:
    """数据采集器"""

    def __init__(self):
        self.running = False
        self.market_cache = get_market_cache()
        self.price_cache = get_price_cache()

    async def start(self):
        """启动采集"""
        self.running = True
        logger.info("数据采集器已启动")

    async def stop(self):
        """停止采集"""
        self.running = False
        logger.info("数据采集器已停止")

    async def collect_markets(self) -> List[Dict]:
        """采集市场数据"""
        try:
            client = await get_client()
            markets = await client.get_markets()
            logger.debug(f"采集到 {len(markets)} 个市场")
            return markets
        except Exception as e:
            logger.error(f"采集市场数据失败: {e}")
            return []

    async def collect_prices(self, market_id: str) -> Dict:
        """采集价格数据"""
        try:
            # 检查缓存
            cache_key = f"price:{market_id}"
            cached = await self.price_cache.get(cache_key)
            if cached:
                return cached

            # 获取新数据
            client = await get_client()
            yes_price = await client.get_price(market_id, 'YES')
            no_price = await client.get_price(market_id, 'NO')

            prices = {
                'market_id': market_id,
                'yes': yes_price,
                'no': no_price
            }

            # 缓存
            await self.price_cache.set(cache_key, prices)
            return prices
        except Exception as e:
            logger.error(f"采集价格失败: {e}")
            return {}
