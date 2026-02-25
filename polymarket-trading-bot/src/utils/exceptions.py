"""自定义异常类"""


class TradingBotException(Exception):
    """交易机器人基础异常"""
    pass


class ConfigurationError(TradingBotException):
    """配置错误"""
    pass


class APIError(TradingBotException):
    """API调用错误"""
    pass


class RateLimitError(APIError):
    """API速率限制错误"""
    pass


class AuthenticationError(APIError):
    """认证错误"""
    pass


class InsufficientBalanceError(TradingBotException):
    """余额不足错误"""
    pass


class OrderExecutionError(TradingBotException):
    """订单执行错误"""
    pass


class RiskLimitExceeded(TradingBotException):
    """超过风险限制"""
    pass


class CircuitBreakerTriggered(TradingBotException):
    """熔断器触发"""
    pass


class DatabaseError(TradingBotException):
    """数据库错误"""
    pass


class ValidationError(TradingBotException):
    """数据验证错误"""
    pass


class MarketDataError(TradingBotException):
    """市场数据错误"""
    pass


class StrategyError(TradingBotException):
    """策略执行错误"""
    pass
