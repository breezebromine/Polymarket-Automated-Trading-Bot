"""套利策略"""
from typing import List, Dict
from loguru import logger
from .base_strategy import BaseStrategy
from .opportunity_evaluator import OpportunityEvaluator
from ..utils.config import get_config

class ArbitrageStrategy(BaseStrategy):
    """YES/NO套利策略"""
    
    def __init__(self):
        super().__init__("arbitrage")
        self.config = get_config()
        self.evaluator = OpportunityEvaluator(
            min_profit=self.config.arbitrage.min_profit,
            fee_rate=self.config.arbitrage.fee_rate
        )
    
    async def generate_signals(self, market_data: List[Dict]) -> List[Dict]:
        """生成套利信号"""
        signals = []
        
        for market in market_data:
            opportunity = await self.detect_opportunity(market)
            if opportunity:
                signal = await self.create_signal(opportunity)
                if signal:
                    signals.append(signal)
        
        return signals
    
    async def detect_opportunity(self, market: Dict) -> Dict:
        """检测套利机会"""
        try:
            yes_price = market.get('yes_price', 0.5)
            no_price = market.get('no_price', 0.5)
            
            # YES + NO 应该等于 1.0
            total_price = yes_price + no_price
            spread = abs(1.0 - total_price)
            
            # 考虑手续费
            fee_cost = 2 * self.config.arbitrage.fee_rate
            net_spread = spread - fee_cost
            
            if net_spread > self.config.arbitrage.min_spread:
                opportunity = {
                    'market_id': market.get('id'),
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'spread': net_spread,
                    'expected_profit': net_spread * 100,  # 假设$100投入
                    'max_size': market.get('liquidity', 1000)
                }
                
                if self.evaluator.is_viable(opportunity):
                    logger.info(f"发现套利机会: {market.get('id')}, 价差={net_spread:.3f}")
                    return opportunity
        
        except Exception as e:
            logger.error(f"检测套利失败: {e}")
        
        return None
    
    async def create_signal(self, opportunity: Dict) -> Dict:
        """创建交易信号"""
        return {
            'strategy': self.name,
            'market_id': opportunity['market_id'],
            'type': 'arbitrage',
            'actions': [
                {'outcome': 'YES', 'side': 'BUY', 'price': opportunity['yes_price'], 'size': 100},
                {'outcome': 'NO', 'side': 'BUY', 'price': opportunity['no_price'], 'size': 100}
            ],
            'expected_profit': opportunity['expected_profit']
        }
    
    async def on_market_data(self, data: Dict):
        """处理市场数据"""
        pass
