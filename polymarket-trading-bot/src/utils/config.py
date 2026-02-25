"""配置管理模块"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

from .exceptions import ConfigurationError


class APIConfig(BaseModel):
    """API配置"""
    polymarket_api_key: Optional[str] = None
    polymarket_api_secret: Optional[str] = None
    polymarket_passphrase: Optional[str] = None
    polymarket_base_url: str = "https://clob.polymarket.com"
    polymarket_ws_url: str = "wss://ws-subscriptions-clob.polymarket.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    requests_per_second: int = 10
    burst_size: int = 20


class DatabaseConfig(BaseModel):
    """数据库配置"""
    type: str = "sqlite"
    sqlite_path: str = "data/polymarket.db"
    postgresql_url: Optional[str] = None
    pool_size: int = 10


class TradingConfig(BaseModel):
    """交易配置"""
    enabled: bool = Field(default=False, description="是否启用交易")
    dry_run: bool = Field(default=True, description="模拟交易模式")
    markets: list = Field(default_factory=list, description="监控的市场列表")
    update_interval: int = Field(default=5, description="数据更新间隔(秒)")
    order_timeout: int = Field(default=60, description="订单超时时间(秒)")


class RiskConfig(BaseModel):
    """风险管理配置"""
    max_position_size: float = Field(default=1000, description="单个市场最大头寸(USD)")
    max_total_exposure: float = Field(default=5000, description="总敞口限制(USD)")
    daily_loss_limit: float = Field(default=500, description="每日最大亏损(USD)")
    max_trades_per_day: int = Field(default=100, description="每日最大交易次数")
    min_liquidity: float = Field(default=1000, description="最小市场流动性要求(USD)")


class ArbitrageConfig(BaseModel):
    """套利策略配置"""
    min_spread: float = Field(default=0.02, description="最小价差(百分比)")
    min_profit: float = Field(default=5, description="最小预期利润(USD)")
    max_execution_time: int = Field(default=10, description="最大执行时间(秒)")
    include_fees: bool = Field(default=True, description="是否考虑手续费")
    fee_rate: float = Field(default=0.001, description="手续费率")
    slippage_tolerance: float = Field(default=0.005, description="滑点容忍度")


class Config:
    """主配置类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径,默认为config/config.yaml
        """
        # 加载环境变量
        load_dotenv()

        # 设置项目根目录
        self.root_dir = Path(__file__).parent.parent.parent

        # 加载配置文件
        if config_path is None:
            config_path = self.root_dir / "config" / "config.yaml"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise ConfigurationError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config_data = yaml.safe_load(f)

        # 加载各模块配置
        self._load_configs()

    def _load_configs(self):
        """加载各模块配置"""
        # 系统配置
        system_config = self.config_data.get('system', {})
        self.environment = system_config.get('environment', 'development')
        self.debug = system_config.get('debug', True)
        self.log_level = os.getenv('LOG_LEVEL', system_config.get('log_level', 'INFO'))

        # API配置
        api_config = self.config_data.get('api', {})
        self.api = APIConfig(
            polymarket_api_key=os.getenv('POLYMARKET_API_KEY'),
            polymarket_api_secret=os.getenv('POLYMARKET_API_SECRET'),
            polymarket_passphrase=os.getenv('POLYMARKET_PASSPHRASE'),
            polymarket_base_url=api_config.get('polymarket', {}).get('base_url',
                                                                      'https://clob.polymarket.com'),
            polymarket_ws_url=api_config.get('polymarket', {}).get('ws_url',
                                                                    'wss://ws-subscriptions-clob.polymarket.com'),
            timeout=api_config.get('polymarket', {}).get('timeout', 30),
            max_retries=api_config.get('polymarket', {}).get('max_retries', 3),
            retry_delay=api_config.get('polymarket', {}).get('retry_delay', 1.0),
            requests_per_second=api_config.get('rate_limit', {}).get('requests_per_second', 10),
            burst_size=api_config.get('rate_limit', {}).get('burst_size', 20)
        )

        # 数据库配置
        db_config = self.config_data.get('database', {})
        db_type = db_config.get('type', 'sqlite')
        self.database = DatabaseConfig(
            type=db_type,
            sqlite_path=db_config.get('sqlite', {}).get('path', 'data/polymarket.db'),
            postgresql_url=os.getenv('DATABASE_URL',
                                    db_config.get('postgresql', {}).get('url')),
            pool_size=db_config.get('postgresql', {}).get('pool_size', 10)
        )

        # 交易配置
        trading_config = self.config_data.get('trading', {})
        self.trading = TradingConfig(
            enabled=self._get_bool_env('TRADING_ENABLED', trading_config.get('enabled', False)),
            dry_run=self._get_bool_env('DRY_RUN', trading_config.get('dry_run', True)),
            markets=trading_config.get('markets', []),
            update_interval=trading_config.get('update_interval', 5),
            order_timeout=trading_config.get('order_timeout', 60)
        )

        # 加载风险配置
        self._load_risk_config()

        # 加载策略配置
        self._load_strategy_config()

        # Web3配置
        self.eth_private_key = os.getenv('ETH_PRIVATE_KEY')
        self.eth_rpc_url = os.getenv('ETH_RPC_URL', 'https://polygon-rpc.com')

        # 告警配置
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.sentry_dsn = os.getenv('SENTRY_DSN')

    def _load_risk_config(self):
        """加载风险配置"""
        risk_config_path = self.root_dir / "config" / "risk_params.yaml"
        if risk_config_path.exists():
            with open(risk_config_path, 'r', encoding='utf-8') as f:
                risk_data = yaml.safe_load(f)
        else:
            risk_data = self.config_data.get('risk', {})

        self.risk = RiskConfig(
            max_position_size=risk_data.get('max_position_size', 1000),
            max_total_exposure=risk_data.get('max_total_exposure', 5000),
            daily_loss_limit=risk_data.get('daily_loss_limit', 500),
            max_trades_per_day=risk_data.get('max_trades_per_day', 100),
            min_liquidity=risk_data.get('min_liquidity', 1000)
        )

    def _load_strategy_config(self):
        """加载策略配置"""
        strategy_config_path = self.root_dir / "config" / "strategies.yaml"
        if strategy_config_path.exists():
            with open(strategy_config_path, 'r', encoding='utf-8') as f:
                strategy_data = yaml.safe_load(f)
        else:
            strategy_data = self.config_data.get('arbitrage', {})

        arbitrage_config = strategy_data.get('arbitrage', strategy_data)
        self.arbitrage = ArbitrageConfig(
            min_spread=arbitrage_config.get('min_spread', 0.02),
            min_profit=arbitrage_config.get('min_profit', 5),
            max_execution_time=arbitrage_config.get('max_execution_time', 10),
            include_fees=arbitrage_config.get('include_fees', True),
            fee_rate=arbitrage_config.get('fee_rate', 0.001),
            slippage_tolerance=arbitrage_config.get('slippage_tolerance', 0.005)
        )

    def _get_bool_env(self, key: str, default: bool) -> bool:
        """从环境变量获取布尔值"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')

    def validate(self):
        """验证配置"""
        errors = []

        # 验证交易启用时必须提供API密钥
        if self.trading.enabled and not self.trading.dry_run:
            if not self.api.polymarket_api_key:
                errors.append("交易已启用但未提供POLYMARKET_API_KEY")
            if not self.api.polymarket_api_secret:
                errors.append("交易已启用但未提供POLYMARKET_API_SECRET")
            if not self.eth_private_key:
                errors.append("交易已启用但未提供ETH_PRIVATE_KEY")

        # 验证风险参数合理性
        if self.risk.max_position_size > self.risk.max_total_exposure:
            errors.append("单个市场最大头寸不能大于总敞口限制")

        if self.risk.daily_loss_limit > self.risk.max_total_exposure:
            errors.append("每日最大亏损不能大于总敞口限制")

        # 验证套利参数
        if self.arbitrage.min_spread <= 0:
            errors.append("最小价差必须大于0")

        if self.arbitrage.min_profit <= 0:
            errors.append("最小利润必须大于0")

        if errors:
            raise ConfigurationError("配置验证失败:\n" + "\n".join(f"- {e}" for e in errors))

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value


# 全局配置实例
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    获取全局配置实例

    Args:
        config_path: 配置文件路径

    Returns:
        Config: 配置实例
    """
    global _config
    if _config is None:
        _config = Config(config_path)
        _config.validate()
    return _config


def reload_config(config_path: Optional[str] = None):
    """
    重新加载配置

    Args:
        config_path: 配置文件路径
    """
    global _config
    _config = Config(config_path)
    _config.validate()
