"""数据模型定义"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean,
    Text, ForeignKey, Enum as SQLEnum, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class OrderStatus(enum.Enum):
    """订单状态"""
    PENDING = "pending"           # 待提交
    SUBMITTED = "submitted"       # 已提交
    PARTIALLY_FILLED = "partially_filled"  # 部分成交
    FILLED = "filled"             # 完全成交
    CANCELLED = "cancelled"       # 已取消
    REJECTED = "rejected"         # 已拒绝
    EXPIRED = "expired"           # 已过期


class OrderSide(enum.Enum):
    """订单方向"""
    BUY = "buy"
    SELL = "sell"


class OrderType(enum.Enum):
    """订单类型"""
    MARKET = "market"
    LIMIT = "limit"


class Market(Base):
    """市场信息表"""
    __tablename__ = 'markets'

    id = Column(String(100), primary_key=True)
    condition_id = Column(String(100), nullable=False)
    question = Column(Text, nullable=False)
    description = Column(Text)
    end_date = Column(DateTime)

    # 结果选项
    outcomes = Column(Text)  # JSON格式存储

    # 市场状态
    active = Column(Boolean, default=True)
    closed = Column(Boolean, default=False)

    # 流动性和交易量
    liquidity = Column(Float, default=0.0)
    volume = Column(Float, default=0.0)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    prices = relationship("Price", back_populates="market", cascade="all, delete-orphan")
    orderbooks = relationship("OrderBook", back_populates="market", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="market")

    def __repr__(self):
        return f"<Market(id={self.id}, question={self.question[:50]})>"


class Price(Base):
    """价格历史表"""
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String(100), ForeignKey('markets.id'), nullable=False)
    outcome = Column(String(50), nullable=False)  # YES/NO

    # 价格数据
    price = Column(Float, nullable=False)
    bid = Column(Float)
    ask = Column(Float)

    # 时间戳
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    market = relationship("Market", back_populates="prices")

    # 索引
    __table_args__ = (
        Index('idx_market_outcome_time', 'market_id', 'outcome', 'timestamp'),
    )

    def __repr__(self):
        return f"<Price(market={self.market_id}, outcome={self.outcome}, price={self.price})>"


class OrderBook(Base):
    """订单簿快照表"""
    __tablename__ = 'orderbooks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String(100), ForeignKey('markets.id'), nullable=False)
    outcome = Column(String(50), nullable=False)

    # 订单簿数据 (JSON格式)
    bids = Column(Text)  # [[price, size], ...]
    asks = Column(Text)  # [[price, size], ...]

    # 统计信息
    best_bid = Column(Float)
    best_ask = Column(Float)
    spread = Column(Float)
    depth = Column(Float)  # 订单簿深度

    # 时间戳
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    market = relationship("Market", back_populates="orderbooks")

    def __repr__(self):
        return f"<OrderBook(market={self.market_id}, bid={self.best_bid}, ask={self.best_ask})>"


class Order(Base):
    """订单表"""
    __tablename__ = 'orders'

    id = Column(String(100), primary_key=True)
    market_id = Column(String(100), ForeignKey('markets.id'), nullable=False)
    outcome = Column(String(50), nullable=False)

    # 订单信息
    side = Column(SQLEnum(OrderSide), nullable=False)
    type = Column(SQLEnum(OrderType), nullable=False)
    status = Column(SQLEnum(OrderStatus), nullable=False, default=OrderStatus.PENDING)

    # 价格和数量
    price = Column(Float)
    size = Column(Float, nullable=False)
    filled_size = Column(Float, default=0.0)
    remaining_size = Column(Float)

    # 关联信息
    strategy_name = Column(String(50))

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    filled_at = Column(DateTime)

    # 关系
    trades = relationship("Trade", back_populates="order")

    def __repr__(self):
        return f"<Order(id={self.id}, {self.side.value} {self.size}@{self.price}, status={self.status.value})>"


class Trade(Base):
    """成交记录表"""
    __tablename__ = 'trades'

    id = Column(String(100), primary_key=True)
    order_id = Column(String(100), ForeignKey('orders.id'), nullable=False)
    market_id = Column(String(100), ForeignKey('markets.id'), nullable=False)
    outcome = Column(String(50), nullable=False)

    # 成交信息
    side = Column(SQLEnum(OrderSide), nullable=False)
    price = Column(Float, nullable=False)
    size = Column(Float, nullable=False)
    value = Column(Float, nullable=False)  # price * size

    # 费用
    fee = Column(Float, default=0.0)

    # 策略信息
    strategy_name = Column(String(50))

    # 时间戳
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # 关系
    order = relationship("Order", back_populates="trades")
    market = relationship("Market", back_populates="trades")

    def __repr__(self):
        return f"<Trade(id={self.id}, {self.side.value} {self.size}@{self.price})>"


class Position(Base):
    """持仓表"""
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    market_id = Column(String(100), ForeignKey('markets.id'), nullable=False)
    outcome = Column(String(50), nullable=False)

    # 持仓信息
    size = Column(Float, nullable=False)  # 正数=持有YES,负数=持有NO
    avg_entry_price = Column(Float, nullable=False)
    current_price = Column(Float)

    # 盈亏
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)

    # 策略信息
    strategy_name = Column(String(50))

    # 时间戳
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)

    # 唯一约束
    __table_args__ = (
        UniqueConstraint('market_id', 'outcome', 'strategy_name', name='uq_position'),
    )

    def __repr__(self):
        return f"<Position(market={self.market_id}, outcome={self.outcome}, size={self.size}, pnl={self.unrealized_pnl})>"


class ArbitrageOpportunity(Base):
    """套利机会记录表"""
    __tablename__ = 'arbitrage_opportunities'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 市场信息
    market_id = Column(String(100), ForeignKey('markets.id'), nullable=False)
    market_id_2 = Column(String(100), ForeignKey('markets.id'))  # 跨市场套利时使用

    # 套利类型
    type = Column(String(50), nullable=False)  # yes_no, cross_market等

    # 价格信息
    yes_price = Column(Float)
    no_price = Column(Float)
    spread = Column(Float, nullable=False)

    # 利润估算
    expected_profit = Column(Float, nullable=False)
    expected_profit_pct = Column(Float)

    # 流动性
    max_size = Column(Float)

    # 评分
    score = Column(Float)  # 机会评分 0-1

    # 执行状态
    executed = Column(Boolean, default=False)
    execution_result = Column(Text)  # JSON格式

    # 时间戳
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    executed_at = Column(DateTime)

    def __repr__(self):
        return f"<ArbitrageOpportunity(market={self.market_id}, spread={self.spread}, profit={self.expected_profit})>"


class PerformanceMetric(Base):
    """性能指标表"""
    __tablename__ = 'performance_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 时间周期
    date = Column(DateTime, nullable=False, index=True)
    period = Column(String(20), nullable=False)  # daily, weekly, monthly

    # 交易统计
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0.0)

    # 盈亏统计
    total_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)

    # 风险指标
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float)

    # 资金使用
    avg_position_size = Column(Float)
    max_exposure = Column(Float)

    # 策略信息
    strategy_name = Column(String(50))

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('date', 'period', 'strategy_name', name='uq_metric'),
    )

    def __repr__(self):
        return f"<PerformanceMetric(date={self.date}, pnl={self.total_pnl}, trades={self.total_trades})>"


class SystemLog(Base):
    """系统日志表"""
    __tablename__ = 'system_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 日志级别
    level = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR

    # 日志内容
    module = Column(String(50))
    message = Column(Text, nullable=False)
    details = Column(Text)  # JSON格式的详细信息

    # 时间戳
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<SystemLog(level={self.level}, message={self.message[:50]})>"
