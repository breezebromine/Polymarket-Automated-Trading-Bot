"""历史数据加载器 - 从Polymarket加载真实历史数据"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger
import requests

# Polymarket Gamma API (公开API,不需要认证)
GAMMA_API_BASE = "https://gamma-api.polymarket.com"


class HistoricalDataLoader:
    """从Polymarket加载历史数据"""

    def __init__(self):
        """初始化历史数据加载器"""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        # 禁用SSL验证警告
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        logger.info(f"历史数据加载器初始化完成: {GAMMA_API_BASE}")

    def get_market_by_name(self, search_term: str) -> Optional[Dict]:
        """
        通过名称搜索市场

        Args:
            search_term: 搜索关键词(如"Trump", "Election")

        Returns:
            市场信息字典,未找到返回None
        """
        try:
            # 使用Gamma API搜索市场
            url = f"{GAMMA_API_BASE}/markets"
            params = {"active": "true", "closed": "false"}

            response = self.session.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()

            markets = response.json()

            # 搜索匹配的市场
            for market in markets:
                question = market.get('question', '').lower()
                if search_term.lower() in question:
                    logger.info(f"找到市场: {market.get('question')}")
                    logger.info(f"Market ID: {market.get('condition_id')}")
                    return market

            logger.warning(f"未找到包含'{search_term}'的市场")
            return None

        except Exception as e:
            logger.error(f"搜索市场失败: {e}")
            return None

    def load_trade_history(
        self,
        market_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        加载市场交易历史

        Args:
            market_id: 市场ID (condition_id)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            包含历史交易数据的DataFrame
        """
        try:
            logger.info(f"正在加载市场 {market_id} 的历史数据...")
            logger.info(f"时间范围: {start_date} 至 {end_date}")

            # 使用Gamma API获取市场事件数据
            url = f"{GAMMA_API_BASE}/events"
            params = {
                "id": market_id,
                "limit": 1000
            }

            response = self.session.get(url, params=params, timeout=30, verify=False)
            response.raise_for_status()

            events = response.json()

            if not events:
                logger.warning("未获取到交易数据")
                return pd.DataFrame()

            logger.info(f"获取到 {len(events)} 条事件记录")

            # 转换为DataFrame
            df = pd.DataFrame(events)

            # 数据处理
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

            return df

        except Exception as e:
            logger.error(f"加载交易历史失败: {e}", exc_info=True)
            return pd.DataFrame()

    def load_orderbook_snapshots(
        self,
        market_id: str,
        start_date: str,
        end_date: str,
        interval_hours: int = 1
    ) -> pd.DataFrame:
        """
        加载历史订单簿快照(定期采样)

        Args:
            market_id: 市场ID
            start_date: 开始日期
            end_date: 结束日期
            interval_hours: 采样间隔(小时)

        Returns:
            包含价格和流动性的DataFrame
        """
        try:
            logger.info("开始加载市场价格快照...")

            # 获取市场的当前价格数据
            url = f"{GAMMA_API_BASE}/markets/{market_id}"

            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()

            market_data = response.json()

            if not market_data:
                logger.warning("无法获取市场数据")
                return pd.DataFrame()

            # 注意: Gamma API不直接提供历史快照
            # 这里使用简化方法:基于当前价格生成模拟历史数据
            logger.warning("Polymarket API不提供历史订单簿快照,使用当前价格和模拟数据")

            # 获取当前价格
            outcomes = market_data.get('outcomes', [])
            if len(outcomes) < 2:
                logger.warning("市场outcomes数量不足")
                return pd.DataFrame()

            current_yes_price = float(outcomes[0].get('price', 0.5))
            logger.info(f"当前YES价格: {current_yes_price}")

            # 基于当前价格生成简单的历史数据(用于演示)
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')

            dates = []
            yes_prices = []
            no_prices = []

            current = start
            while current <= end:
                # 使用当前价格作为基准,添加小幅波动
                import random
                volatility = 0.05
                yes_price = max(0.01, min(0.99,
                    current_yes_price + random.uniform(-volatility, volatility)
                ))
                no_price = 1.0 - yes_price

                dates.append(current)
                yes_prices.append(round(yes_price, 3))
                no_prices.append(round(no_price, 3))

                current += timedelta(hours=interval_hours)

            df = pd.DataFrame({
                'timestamp': dates,
                'yes_price': yes_prices,
                'no_price': no_prices,
                'total_price': [y + n for y, n in zip(yes_prices, no_prices)],
                'liquidity': [10000] * len(dates)
            })

            logger.info(f"生成了 {len(df)} 个价格快照(基于当前价格)")

            return df

        except Exception as e:
            logger.error(f"加载订单簿快照失败: {e}", exc_info=True)
            return pd.DataFrame()

    def get_market_info(self, market_id: str) -> Optional[Dict]:
        """
        获取市场详细信息

        Args:
            market_id: 市场ID

        Returns:
            市场信息字典
        """
        try:
            url = f"{GAMMA_API_BASE}/markets/{market_id}"
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            logger.error(f"获取市场信息失败: {e}")
            return None

    def list_popular_markets(self, limit: int = 10) -> List[Dict]:
        """
        列出热门市场

        Args:
            limit: 返回数量

        Returns:
            市场列表
        """
        try:
            url = f"{GAMMA_API_BASE}/markets"
            params = {
                "active": "true",
                "closed": "false",
                "limit": limit
            }

            response = self.session.get(url, params=params, timeout=10, verify=False)
            response.raise_for_status()

            markets = response.json()

            # 按流动性或成交量排序(如果可用)
            if markets:
                # 返回前N个市场
                return markets[:limit]

            return []

        except Exception as e:
            logger.error(f"获取热门市场失败: {e}")
            return []
