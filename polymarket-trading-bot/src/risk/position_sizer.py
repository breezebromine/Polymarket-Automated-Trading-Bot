"""仓位计算器"""
from ..utils.config import get_config

class PositionSizer:
    """仓位计算"""
    
    def __init__(self):
        self.config = get_config()
    
    def calculate_size(self, signal: dict, account_balance: float) -> float:
        """计算交易数量"""
        # 简单的固定金额方法
        fixed_amount = 100  # $100 per trade
        price = signal.get('price', 1.0)
        
        if price > 0:
            size = fixed_amount / price
            return min(size, account_balance * 0.1)  # 不超过账户10%
        
        return 0
