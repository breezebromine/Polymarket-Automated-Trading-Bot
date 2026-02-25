"""熔断器"""
from loguru import logger

class CircuitBreaker:
    """熔断器 - 防止连续亏损"""
    
    def __init__(self, max_consecutive_losses: int = 5):
        self.max_consecutive_losses = max_consecutive_losses
        self.consecutive_losses = 0
        self.is_triggered = False
    
    def check(self) -> bool:
        """检查熔断状态"""
        if self.is_triggered:
            logger.error("🛑 熔断器已触发! 交易已暂停")
        return not self.is_triggered
    
    def record_trade(self, pnl: float):
        """记录交易结果"""
        if pnl < 0:
            self.consecutive_losses += 1
            logger.warning(f"连续亏损: {self.consecutive_losses}/{self.max_consecutive_losses}")
            
            if self.consecutive_losses >= self.max_consecutive_losses:
                self.trigger()
        else:
            # 盈利则重置计数器
            if self.consecutive_losses > 0:
                logger.info(f"连续亏损结束,重置计数器")
            self.consecutive_losses = 0
    
    def trigger(self):
        """触发熔断"""
        self.is_triggered = True
        logger.error(f"🔴 熔断器触发! 连续亏损{self.consecutive_losses}次")
    
    def reset(self):
        """重置熔断器"""
        self.is_triggered = False
        self.consecutive_losses = 0
        logger.info("✓ 熔断器已重置")
