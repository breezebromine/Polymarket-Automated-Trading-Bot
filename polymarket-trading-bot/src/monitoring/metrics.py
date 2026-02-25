"""性能指标监控"""

from typing import Dict, List
from datetime import datetime
from loguru import logger


class MetricsCollector:
    """性能指标采集器"""

    def __init__(self):
        self.metrics = {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'max_drawdown': 0.0,
            'start_time': datetime.now()
        }

    def record_trade(self, trade: Dict):
        """记录交易"""
        self.metrics['total_trades'] += 1

        pnl = trade.get('pnl', 0)
        self.metrics['total_pnl'] += pnl

        if pnl > 0:
            self.metrics['winning_trades'] += 1
        elif pnl < 0:
            self.metrics['losing_trades'] += 1

    def get_win_rate(self) -> float:
        """获取胜率"""
        total = self.metrics['total_trades']
        if total == 0:
            return 0.0
        return self.metrics['winning_trades'] / total

    def get_metrics(self) -> Dict:
        """获取所有指标"""
        return {
            **self.metrics,
            'win_rate': self.get_win_rate(),
            'avg_pnl': self.metrics['total_pnl'] / max(self.metrics['total_trades'], 1)
        }

    def log_summary(self):
        """记录统计摘要"""
        metrics = self.get_metrics()
        logger.info("=" * 60)
        logger.info("交易统计摘要")
        logger.info("=" * 60)
        logger.info(f"总交易次数: {metrics['total_trades']}")
        logger.info(f"胜率: {metrics['win_rate']:.2%}")
        logger.info(f"总盈亏: ${metrics['total_pnl']:.2f}")
        logger.info(f"平均盈亏: ${metrics['avg_pnl']:.2f}")
        logger.info("=" * 60)


_metrics: MetricsCollector = None


def get_metrics_collector() -> MetricsCollector:
    """获取全局指标采集器"""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics
