"""手续费模型 — A 股标准: 佣金双边 + 印花税卖方 + 过户费双边"""
from __future__ import annotations
from dataclasses import dataclass


class CostModel:
    def commission(self, side: str, price: float, qty: int) -> float:
        raise NotImplementedError


@dataclass
class AShareCostModel(CostModel):
    """A 股标准费率（默认券商常见值，可按账户实际调整）"""
    commission_rate: float = 0.00025   # 万 2.5 佣金（双边），最低 5 元
    min_commission: float = 5.0
    stamp_tax: float = 0.0005          # 印花税 0.05%（卖方）
    transfer_fee: float = 0.00001      # 过户费 0.001%（双边，沪深统一）

    def commission(self, side: str, price: float, qty: int) -> float:
        notional = price * qty
        comm = max(notional * self.commission_rate, self.min_commission)
        transfer = notional * self.transfer_fee
        stamp = notional * self.stamp_tax if side == "sell" else 0.0
        return comm + transfer + stamp
