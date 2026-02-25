"""仓位跟踪器"""
from typing import Dict, List
from loguru import logger

class PositionTracker:
    """仓位跟踪"""
    
    def __init__(self):
        self.positions: Dict[str, Dict] = {}
    
    async def update_position(self, trade: Dict):
        """更新仓位"""
        market_id = trade.get('market_id')
        outcome = trade.get('outcome', 'YES')
        key = f"{market_id}:{outcome}"
        
        if key not in self.positions:
            self.positions[key] = {
                'market_id': market_id,
                'outcome': outcome,
                'size': 0,
                'avg_price': 0,
                'unrealized_pnl': 0
            }
        
        position = self.positions[key]
        size = trade.get('size', 0)
        price = trade.get('price', 0)
        
        # 更新仓位
        if trade.get('side') == 'BUY':
            position['size'] += size
        else:
            position['size'] -= size
        
        logger.debug(f"仓位更新: {key} = {position['size']}")
    
    async def get_positions(self) -> List[Dict]:
        """获取所有持仓"""
        return list(self.positions.values())
    
    async def get_position_value(self) -> float:
        """获取持仓总价值"""
        return sum(p.get('size', 0) * p.get('avg_price', 0) for p in self.positions.values())
    
    async def get_total_pnl(self) -> float:
        """获取总盈亏"""
        return sum(p.get('unrealized_pnl', 0) for p in self.positions.values())
