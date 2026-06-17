"""持仓 + 组合（含 T+1 可卖数量）"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from datetime import date


@dataclass
class Position:
    code: str
    qty: int = 0              # 总持仓
    avail_qty: int = 0        # 可卖数量（T+1 → 当日买入冻结到次日）
    avg_cost: float = 0.0     # 持仓均价
    last_price: float = 0.0

    @property
    def market_value(self) -> float:
        return self.qty * self.last_price

    @property
    def pnl(self) -> float:
        return (self.last_price - self.avg_cost) * self.qty


@dataclass
class Portfolio:
    cash: float
    positions: Dict[str, Position] = field(default_factory=dict)

    def market_value(self) -> float:
        return sum(p.market_value for p in self.positions.values())

    def total_value(self) -> float:
        return self.cash + self.market_value()

    def get_position(self, code: str) -> Position:
        if code not in self.positions:
            self.positions[code] = Position(code=code)
        return self.positions[code]

    def on_new_day(self):
        """T+1 解冻 — 每个新交易日开盘前调用，把昨日及之前买入的全部转为可卖"""
        for p in self.positions.values():
            p.avail_qty = p.qty

    def update_market_prices(self, prices: Dict[str, float]):
        for code, p in self.positions.items():
            if code in prices:
                p.last_price = prices[code]
