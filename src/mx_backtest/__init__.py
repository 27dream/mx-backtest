"""mx-backtest — A 股事件驱动回测引擎

特性：
- T+1 持仓约束（今日买，次日才能卖）
- 涨跌停板限制（涨停不可买，跌停不可卖）
- 停牌检测（无成交量则跳过）
- 前复权 / 后复权
- 手续费 + 印花税 + 过户费
- 滑点模型（固定 / 比例 / 成交量加权）
- 事件驱动 Engine + 向量化 Backtest 双模式
"""
from .engine import BacktestEngine, BacktestResult
from .broker import Broker, Order, Trade, OrderSide, OrderStatus
from .portfolio import Portfolio, Position
from .data import BarData, DataFeed, CSVFeed, DataFrameFeed
from .strategy import Strategy
from .costs import CostModel, AShareCostModel
from .slippage import Slippage, FixedSlippage, PercentSlippage
from .metrics import compute_metrics, Metrics

__version__ = "0.1.0"

__all__ = [
    "BacktestEngine", "BacktestResult",
    "Broker", "Order", "Trade", "OrderSide", "OrderStatus",
    "Portfolio", "Position",
    "BarData", "DataFeed", "CSVFeed", "DataFrameFeed",
    "Strategy",
    "CostModel", "AShareCostModel",
    "Slippage", "FixedSlippage", "PercentSlippage",
    "compute_metrics", "Metrics",
]
