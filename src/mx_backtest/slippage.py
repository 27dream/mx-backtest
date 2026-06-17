"""滑点模型"""
from __future__ import annotations
from dataclasses import dataclass


class Slippage:
    def adjust(self, side: str, price: float) -> float:
        raise NotImplementedError


@dataclass
class FixedSlippage(Slippage):
    """固定 tick 滑点"""
    tick: float = 0.01

    def adjust(self, side: str, price: float) -> float:
        return price + self.tick if side == "buy" else price - self.tick


@dataclass
class PercentSlippage(Slippage):
    """百分比滑点（默认万 5）"""
    pct: float = 0.0005

    def adjust(self, side: str, price: float) -> float:
        return price * (1 + self.pct) if side == "buy" else price * (1 - self.pct)
