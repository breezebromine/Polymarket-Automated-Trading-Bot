"""跨市场套利策略"""
from typing import List, Dict
from .base_strategy import BaseStrategy
from loguru import logger

class CrossMarketArbitrageStrategy(BaseStrategy):
    """跨市场套利"""
    
    def __init__(self):
        super().__init__("cross_market_arbitrage")
    
    async def generate_signals(self, market_data: List[Dict]) -> List[Dict]:
        """生成跨市场套利信号"""
        # TODO: 实现跨市场套利逻辑
        return []
    
    async def on_market_data(self, data: Dict):
        """处理市场数据"""
        pass
