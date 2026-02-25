"""策略基类"""
from abc import ABC, abstractmethod
from typing import List, Dict

class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def generate_signals(self, market_data: List[Dict]) -> List[Dict]:
        """生成交易信号"""
        pass
    
    @abstractmethod
    async def on_market_data(self, data: Dict):
        """处理市场数据更新"""
        pass
    
    def get_params(self) -> Dict:
        """获取策略参数"""
        return {'name': self.name}
