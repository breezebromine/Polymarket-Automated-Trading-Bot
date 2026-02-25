"""回测脚本 - 特朗普竞选市场"""
import sys
import asyncio
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.backtesting.backtest_engine import BacktestEngine

async def run_backtest(start_date: str, end_date: str, market: str = "trump_election", use_real_data: bool = False):
    try:
        logger.info("=" * 60)
        logger.info("🔬 Polymarket套利策略回测")
        logger.info("=" * 60)
        logger.info(f"市场: {market}")
        logger.info(f"时间: {start_date} 至 {end_date}")
        logger.info(f"数据源: {'真实数据(Polymarket API)' if use_real_data else '模拟数据'}")
        logger.info("=" * 60)

        engine = BacktestEngine(use_real_data=use_real_data)
        logger.info("加载历史数据...")
        market_data = engine.load_historical_data(market, start_date, end_date)
        logger.info(f"✓ {len(market_data)} 个数据点")

        logger.info("-" * 60)
        arb_opps = len(market_data[(market_data['total_price'] < 0.98) | (market_data['total_price'] > 1.02)])
        logger.info(f"潜在套利机会: {arb_opps} 次 ({arb_opps/len(market_data)*100:.1f}%)")
        logger.info("-" * 60)

        results = await engine.run_backtest(market_data)
        engine.print_results(results)
        return 0
    except Exception as e:
        logger.error(f"回测失败: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='运行Polymarket策略回测')
    parser.add_argument('--start', default='2024-01-01', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', default='2024-11-05', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--market', default='trump', help='市场ID或搜索关键词 (如: trump, election)')
    parser.add_argument('--real', action='store_true', help='使用真实数据(需要联网)')
    args = parser.parse_args()
    exit_code = asyncio.run(run_backtest(args.start, args.end, args.market, args.real))
    sys.exit(exit_code)
