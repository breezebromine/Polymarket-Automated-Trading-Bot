"""风险管理器"""
from loguru import logger
from ..utils.config import get_config
from ..utils.exceptions import RiskLimitExceeded

class RiskManager:
    """风险管理"""
    
    def __init__(self):
        self.config = get_config()
        self.daily_pnl = 0
        self.trade_count_today = 0
        self.total_exposure = 0
    
    def check_trade_allowed(self, signal: dict) -> bool:
        """检查交易是否允许"""
        try:
            # 检查每日损失限制
            if abs(self.daily_pnl) >= self.config.risk.daily_loss_limit:
                logger.warning(f"⚠️ 达到每日损失限制: {self.daily_pnl}")
                return False
            
            # 检查交易次数
            if self.trade_count_today >= self.config.risk.max_trades_per_day:
                logger.warning(f"⚠️ 达到每日交易次数限制: {self.trade_count_today}")
                return False
            
            # 检查单笔仓位大小
            position_size = signal.get('size', 0) * signal.get('price', 1)
            if position_size > self.config.risk.max_position_size:
                logger.warning(f"⚠️ 超过单笔仓位限制: {position_size}")
                return False
            
            # 检查总敞口
            if self.total_exposure + position_size > self.config.risk.max_total_exposure:
                logger.warning(f"⚠️ 超过总敞口限制: {self.total_exposure + position_size}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"风险检查失败: {e}")
            return False
    
    def record_trade(self, pnl: float, size: float):
        """记录交易"""
        self.daily_pnl += pnl
        self.trade_count_today += 1
        logger.info(f"今日PnL: {self.daily_pnl:.2f}, 交易次数: {self.trade_count_today}")
    
    def reset_daily(self):
        """重置每日统计"""
        self.daily_pnl = 0
        self.trade_count_today = 0
        logger.info("每日风险统计已重置")
