"""套利机会评估器"""
from typing import Dict
from loguru import logger

class OpportunityEvaluator:
    """评估套利机会质量"""
    
    def __init__(self, min_profit: float = 5.0, fee_rate: float = 0.001):
        self.min_profit = min_profit
        self.fee_rate = fee_rate
    
    def evaluate(self, opportunity: Dict) -> float:
        """
        评估机会得分 (0-1)
        
        考虑因素:
        - 预期利润
        - 价差大小
        - 市场流动性
        """
        profit = opportunity.get('expected_profit', 0)
        spread = opportunity.get('spread', 0)
        liquidity = opportunity.get('max_size', 0)
        
        # 基础评分
        if profit < self.min_profit:
            return 0
        
        # 利润得分 (0-0.5)
        profit_score = min(profit / 50, 0.5)
        
        # 价差得分 (0-0.3)
        spread_score = min(spread / 0.1, 0.3)
        
        # 流动性得分 (0-0.2)
        liquidity_score = min(liquidity / 10000, 0.2)
        
        total_score = profit_score + spread_score + liquidity_score
        return min(total_score, 1.0)
    
    def is_viable(self, opportunity: Dict) -> bool:
        """判断机会是否可行"""
        profit = opportunity.get('expected_profit', 0)
        # 简化判断:只要预期利润大于最小利润要求即可
        return profit >= self.min_profit
