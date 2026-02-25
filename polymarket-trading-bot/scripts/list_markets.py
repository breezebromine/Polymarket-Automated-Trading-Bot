"""列出Polymarket可用市场"""
import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.data.historical_loader import HistoricalDataLoader


def list_popular_markets():
    """列出热门市场"""
    try:
        logger.info("=" * 80)
        logger.info("📊 Polymarket热门市场")
        logger.info("=" * 80)

        loader = HistoricalDataLoader()
        markets = loader.list_popular_markets(limit=20)

        if not markets:
            logger.warning("未获取到市场数据")
            return 1

        logger.info(f"\n找到 {len(markets)} 个热门市场:\n")

        for i, market in enumerate(markets, 1):
            question = market.get('question', 'N/A')
            condition_id = market.get('condition_id', 'N/A')
            liquidity = float(market.get('liquidity', 0))
            volume = float(market.get('volume', 0))

            # 截取问题长度
            if len(question) > 70:
                question = question[:67] + "..."

            logger.info(f"{i}. {question}")
            logger.info(f"   Market ID: {condition_id}")
            logger.info(f"   流动性: ${liquidity:,.0f} | 成交量: ${volume:,.0f}")
            logger.info("")

        logger.info("=" * 80)
        logger.info("使用方法:")
        logger.info("  python scripts/run_backtest.py --market '<搜索关键词>' --real")
        logger.info("")
        logger.info("示例:")
        logger.info("  python scripts/run_backtest.py --market 'Trump' --real")
        logger.info("  python scripts/run_backtest.py --market 'Election' --real")
        logger.info("=" * 80)

        return 0

    except ImportError as e:
        logger.error("请先安装依赖: pip install py-clob-client")
        return 1
    except Exception as e:
        logger.error(f"获取市场列表失败: {e}", exc_info=True)
        return 1


def search_market(keyword: str):
    """搜索特定市场"""
    try:
        logger.info("=" * 80)
        logger.info(f"🔍 搜索市场: '{keyword}'")
        logger.info("=" * 80)

        loader = HistoricalDataLoader()
        market = loader.get_market_by_name(keyword)

        if not market:
            logger.warning(f"未找到包含'{keyword}'的市场")
            logger.info("\n尝试使用 'python scripts/list_markets.py' 查看所有可用市场")
            return 1

        logger.info("\n✓ 找到市场:\n")
        logger.info(f"问题: {market.get('question')}")
        logger.info(f"Market ID: {market.get('condition_id')}")
        logger.info(f"流动性: ${float(market.get('liquidity', 0)):,.0f}")
        logger.info(f"成交量: ${float(market.get('volume', 0)):,.0f}")

        outcomes = market.get('outcomes', [])
        if outcomes:
            logger.info(f"\n可选结果:")
            for outcome in outcomes:
                logger.info(f"  - {outcome}")

        logger.info("\n" + "=" * 80)
        logger.info("运行回测:")
        logger.info(f"  python scripts/run_backtest.py --market '{keyword}' --real")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"搜索失败: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="列出或搜索Polymarket市场",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出热门市场
  python scripts/list_markets.py

  # 搜索特定市场
  python scripts/list_markets.py --search Trump
  python scripts/list_markets.py --search "2024 Election"
        """
    )

    parser.add_argument(
        '--search',
        type=str,
        help='搜索市场关键词'
    )

    args = parser.parse_args()

    if args.search:
        exit_code = search_market(args.search)
    else:
        exit_code = list_popular_markets()

    sys.exit(exit_code)
