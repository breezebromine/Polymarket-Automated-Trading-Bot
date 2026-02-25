"""Polymarket自动交易程序主入口"""

import asyncio
import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.utils.config import get_config
from src.monitoring.logger import setup_logging
from src.data.database import init_database
from src.data.collector import DataCollector
from src.api.polymarket_client import PolymarketClient
from src.trading.executor import TradeExecutor
from src.trading.order_manager import OrderManager
from src.trading.position_tracker import PositionTracker
from src.risk.risk_manager import RiskManager
from src.risk.circuit_breaker import CircuitBreaker
from src.strategies.arbitrage_strategy import ArbitrageStrategy
from src.monitoring.metrics import get_metrics_collector


class TradingBot:
    """交易机器人主类"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.running = False
        self.config = get_config()

        # 核心组件
        self.client = None
        self.collector = None
        self.executor = None
        self.order_manager = None
        self.position_tracker = None
        self.risk_manager = None
        self.circuit_breaker = None
        self.strategy = None
        self.metrics = None

    async def initialize(self):
        """初始化所有组件"""
        logger.info("正在初始化组件...")

        # 初始化数据库
        try:
            init_database()
            logger.info("✓ 数据库初始化完成")
        except Exception as e:
            logger.warning(f"数据库初始化失败(将继续运行): {e}")

        # 初始化API客户端
        self.client = PolymarketClient(self.config)
        await self.client.connect()
        logger.info("✓ API客户端初始化完成")

        # 初始化数据采集器
        self.collector = DataCollector()
        await self.collector.start()
        logger.info("✓ 数据采集器初始化完成")

        # 初始化交易执行器
        self.executor = TradeExecutor()
        logger.info("✓ 交易执行器初始化完成")

        # 初始化订单管理
        self.order_manager = OrderManager()
        logger.info("✓ 订单管理器初始化完成")

        # 初始化仓位跟踪
        self.position_tracker = PositionTracker()
        logger.info("✓ 仓位跟踪器初始化完成")

        # 初始化风险管理
        self.risk_manager = RiskManager()
        self.circuit_breaker = CircuitBreaker()
        logger.info("✓ 风险管理器初始化完成")

        # 初始化策略
        self.strategy = ArbitrageStrategy()
        logger.info("✓ 套利策略初始化完成")

        # 初始化监控
        self.metrics = get_metrics_collector()
        logger.info("✓ 监控系统初始化完成")

        logger.info("🎉 所有组件初始化完成!")

    async def run_cycle(self):
        """执行一个交易周期"""
        try:
            # 1. 采集市场数据
            markets = await self.collector.collect_markets()

            # 使用模拟数据(实际使用时会从API获取)
            if len(markets) == 0:
                markets = [{
                    'id': 'demo_market',
                    'yes_price': 0.52,
                    'no_price': 0.46,
                    'liquidity': 5000
                }]

            # 2. 生成交易信号
            signals = await self.strategy.generate_signals(markets)

            # 3. 执行交易
            for signal in signals:
                if not self.circuit_breaker.check():
                    logger.warning("熔断器触发,停止交易")
                    break

                for action in signal.get('actions', []):
                    if self.risk_manager.check_trade_allowed(action):
                        result = await self.executor.execute_signal(action)
                        if result.get('success'):
                            await self.order_manager.track_order(result)
                            await self.position_tracker.update_position(action)
                            self.metrics.record_trade({'pnl': signal.get('expected_profit', 0)})

        except Exception as e:
            logger.error(f"交易周期错误: {e}", exc_info=True)

    async def run(self):
        """主运行循环"""
        self.running = True
        cycle_count = 0

        logger.info("=" * 60)
        logger.info("🚀 交易机器人开始运行")
        logger.info("=" * 60)

        try:
            while self.running:
                cycle_count += 1
                logger.debug(f"--- 交易周期 #{cycle_count} ---")
                await self.run_cycle()
                await asyncio.sleep(self.config.trading.update_interval)

        except KeyboardInterrupt:
            logger.info("收到停止信号...")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """优雅关闭"""
        logger.info("正在关闭...")

        if self.collector:
            await self.collector.stop()

        if self.order_manager:
            await self.order_manager.cancel_all_orders()

        if self.client:
            await self.client.close()

        if self.metrics:
            self.metrics.log_summary()

        logger.info("✓ 程序已安全退出")


async def main(dry_run: bool = True):
    """主程序入口"""
    try:
        config = get_config()
        setup_logging()

        logger.info("=" * 60)
        logger.info("🤖 Polymarket自动交易程序")
        logger.info("=" * 60)
        logger.info(f"版本: v0.1.0")
        logger.info(f"环境: {config.environment}")
        logger.info(f"模拟模式: {dry_run or config.trading.dry_run}")
        logger.info("=" * 60)

        if dry_run or config.trading.dry_run:
            logger.warning("⚠️  当前运行在模拟交易模式")

        bot = TradingBot(dry_run=dry_run)
        await bot.initialize()
        await bot.run()

        return 0

    except Exception as e:
        logger.error(f"程序发生致命错误: {e}", exc_info=True)
        return 1


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Polymarket自动交易程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 模拟交易模式(推荐)
  python src/main.py --dry-run

  # 实盘交易模式(谨慎使用)
  python src/main.py

  # 指定配置文件
  python src/main.py --config config/custom.yaml
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟交易模式,不执行实际交易'
    )

    parser.add_argument(
        '--config',
        type=str,
        help='配置文件路径'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='日志级别'
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # 设置日志级别
    if args.log_level:
        import os
        os.environ['LOG_LEVEL'] = args.log_level

    # 运行主程序
    exit_code = asyncio.run(main(dry_run=args.dry_run))
    sys.exit(exit_code)
