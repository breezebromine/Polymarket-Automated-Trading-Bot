"""回测引擎 - 使用历史数据测试策略"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

from ..strategies.arbitrage_strategy import ArbitrageStrategy
from ..utils.config import get_config
from ..data.historical_loader import HistoricalDataLoader


class BacktestEngine:
    """回测引擎"""

    def __init__(self, use_real_data: bool = False):
        """
        初始化回测引擎

        Args:
            use_real_data: 是否使用真实数据(需要联网)
        """
        self.config = get_config()
        self.strategy = ArbitrageStrategy()
        self.trades = []
        self.equity_curve = []
        self.use_real_data = use_real_data
        self.data_loader = None

        if use_real_data:
            try:
                self.data_loader = HistoricalDataLoader()
                logger.info("✓ 真实数据加载器初始化完成")
            except ImportError:
                logger.warning("无法初始化真实数据加载器,将使用模拟数据")
                self.use_real_data = False

    def load_historical_data(self, market_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        加载历史数据

        Args:
            market_id: 市场ID或搜索关键词
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame with columns: timestamp, yes_price, no_price
        """
        if self.use_real_data and self.data_loader:
            return self._load_real_data(market_id, start_date, end_date)
        else:
            return self._generate_mock_data(market_id, start_date, end_date)

    def _load_real_data(self, market_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """从Polymarket加载真实历史数据"""
        try:
            logger.info(f"正在从Polymarket加载真实数据: {market_id}")

            # 如果market_id不像条件ID,尝试作为搜索词
            if len(market_id) < 20:  # 条件ID通常很长
                market = self.data_loader.get_market_by_name(market_id)
                if market:
                    market_id = market.get('condition_id')
                    logger.info(f"找到市场: {market.get('question')}")
                else:
                    logger.warning(f"未找到市场'{market_id}',使用模拟数据")
                    return self._generate_mock_data(market_id, start_date, end_date)

            # 加载交易历史
            df = self.data_loader.load_orderbook_snapshots(
                market_id, start_date, end_date, interval_hours=1
            )

            if df.empty:
                logger.warning("未获取到真实数据,使用模拟数据")
                return self._generate_mock_data(market_id, start_date, end_date)

            # 确保包含所需列
            required_cols = ['timestamp', 'yes_price', 'no_price', 'total_price']
            if not all(col in df.columns for col in required_cols):
                logger.warning("数据格式不完整,使用模拟数据")
                return self._generate_mock_data(market_id, start_date, end_date)

            # 添加流动性列(如果不存在)
            if 'liquidity' not in df.columns:
                df['liquidity'] = 5000  # 默认值

            logger.info(f"✓ 成功加载 {len(df)} 个真实数据点")
            return df

        except Exception as e:
            logger.error(f"加载真实数据失败: {e},回退到模拟数据")
            return self._generate_mock_data(market_id, start_date, end_date)

    def _generate_mock_data(self, market_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """生成模拟历史数据（基于真实市场特征）"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        dates = []
        yes_prices = []
        no_prices = []

        current = start
        base_yes = 0.50  # 起始价格

        while current <= end:
            # 模拟价格波动（基于真实市场特征）
            import random

            # 随机游走
            base_yes += random.uniform(-0.05, 0.05)
            base_yes = max(0.2, min(0.8, base_yes))  # 限制在合理范围

            # 偶尔出现套利机会（YES + NO != 1.0）
            if random.random() < 0.15:  # 15%的概率出现套利机会
                # 价格不平衡
                yes_price = base_yes + random.uniform(-0.03, 0.03)
                no_price = (1.0 - base_yes) + random.uniform(-0.03, 0.03)

                # 确保价格在合理范围
                yes_price = max(0.01, min(0.99, yes_price))
                no_price = max(0.01, min(0.99, no_price))
            else:
                # 正常市场（价格平衡）
                yes_price = base_yes
                no_price = 1.0 - base_yes + random.uniform(-0.005, 0.005)

            dates.append(current)
            yes_prices.append(round(yes_price, 3))
            no_prices.append(round(no_price, 3))

            current += timedelta(hours=1)  # 每小时一个数据点

        df = pd.DataFrame({
            'timestamp': dates,
            'yes_price': yes_prices,
            'no_price': no_prices,
            'total_price': [y + n for y, n in zip(yes_prices, no_prices)],
            'liquidity': [5000] * len(dates)
        })

        return df

    async def run_backtest(self, market_data: pd.DataFrame) -> Dict:
        """
        运行回测

        Args:
            market_data: 历史市场数据

        Returns:
            回测结果
        """
        logger.info("=" * 60)
        logger.info("开始回测")
        logger.info("=" * 60)

        initial_balance = 10000  # 初始资金$10,000
        balance = initial_balance
        positions = []

        total_trades = 0
        winning_trades = 0
        total_pnl = 0

        logger.info(f"初始资金: ${initial_balance:,.2f}")
        logger.info(f"数据点数: {len(market_data)}")
        logger.info("-" * 60)

        # 遍历历史数据
        for idx, row in market_data.iterrows():
            market = {
                'id': 'trump_election',
                'yes_price': row['yes_price'],
                'no_price': row['no_price'],
                'liquidity': row['liquidity'],
                'timestamp': row['timestamp']
            }

            # 检测套利机会
            opportunity = await self.strategy.detect_opportunity(market)

            if opportunity and balance > 200:  # 至少需要$200才能交易
                # 执行套利交易
                trade_size = min(100, balance * 0.1)  # 每次最多投入$100或10%资金

                # 计算交易成本和利润
                yes_cost = trade_size / 2 * row['yes_price']
                no_cost = trade_size / 2 * row['no_price']
                total_cost = yes_cost + no_cost

                # 手续费
                fee = total_cost * self.config.arbitrage.fee_rate * 2

                # 套利利润（假设最终收敛到1.0）
                profit = trade_size - total_cost - fee

                if profit > 0:
                    balance += profit
                    total_pnl += profit
                    winning_trades += 1

                    trade_record = {
                        'timestamp': row['timestamp'],
                        'yes_price': row['yes_price'],
                        'no_price': row['no_price'],
                        'spread': opportunity['spread'],
                        'size': trade_size,
                        'profit': profit,
                        'balance': balance
                    }

                    self.trades.append(trade_record)
                    total_trades += 1

                    if total_trades <= 5:  # 只显示前5笔交易
                        logger.info(f"交易 #{total_trades}: "
                                  f"价差={opportunity['spread']:.3f}, "
                                  f"利润=${profit:.2f}, "
                                  f"余额=${balance:.2f}")

            # 记录权益曲线
            self.equity_curve.append({
                'timestamp': row['timestamp'],
                'balance': balance
            })

        # 计算统计指标
        final_balance = balance
        total_return = (final_balance - initial_balance) / initial_balance * 100
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
        avg_profit = total_pnl / total_trades if total_trades > 0 else 0

        # 计算最大回撤
        max_balance = initial_balance
        max_drawdown = 0
        for point in self.equity_curve:
            if point['balance'] > max_balance:
                max_balance = point['balance']
            drawdown = (max_balance - point['balance']) / max_balance * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        results = {
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'total_return': total_return,
            'total_pnl': total_pnl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'max_drawdown': max_drawdown,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }

        return results

    def print_results(self, results: Dict):
        """打印回测结果"""
        logger.info("=" * 60)
        logger.info("回测结果")
        logger.info("=" * 60)
        logger.info(f"初始资金:     ${results['initial_balance']:,.2f}")
        logger.info(f"最终资金:     ${results['final_balance']:,.2f}")
        logger.info(f"总收益:       ${results['total_pnl']:,.2f}")
        logger.info(f"收益率:       {results['total_return']:.2f}%")
        logger.info("-" * 60)
        logger.info(f"总交易次数:   {results['total_trades']}")
        logger.info(f"盈利次数:     {results['winning_trades']}")
        logger.info(f"胜率:         {results['win_rate']:.2f}%")
        logger.info(f"平均盈利:     ${results['avg_profit']:.2f}")
        logger.info(f"最大回撤:     {results['max_drawdown']:.2f}%")
        logger.info("=" * 60)
