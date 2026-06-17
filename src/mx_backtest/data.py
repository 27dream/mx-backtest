"""行情数据抽象 — Bar / DataFeed / CSV / DataFrame"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator, Dict, List, Optional, Iterable
import csv
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class BarData:
    """单根 K 线 — 默认前复权价"""
    code: str
    dt: date
    open: float
    high: float
    low: float
    close: float
    volume: float            # 成交量（手 or 股，自洽即可）
    amount: float = 0.0      # 成交额
    pre_close: float = 0.0   # 昨收（用于涨跌停判定）
    is_suspended: bool = False  # 是否停牌

    @property
    def limit_up(self) -> float:
        """涨停价（10%，ST 5%；这里默认 10%，ST 由 Strategy 自行设置 pre_close）"""
        return round(self.pre_close * 1.10, 2) if self.pre_close else float("inf")

    @property
    def limit_down(self) -> float:
        return round(self.pre_close * 0.90, 2) if self.pre_close else 0.0

    @property
    def is_limit_up(self) -> bool:
        """收盘是否一字/封涨停（开=高=低=收=涨停价）"""
        return self.pre_close > 0 and self.high >= self.limit_up - 1e-4 and self.low >= self.limit_up - 1e-4

    @property
    def is_limit_down(self) -> bool:
        return self.pre_close > 0 and self.low <= self.limit_down + 1e-4 and self.high <= self.limit_down + 1e-4


class DataFeed:
    """按时间步推进的 Bar 流 — 子类实现 __iter__"""

    def __iter__(self) -> Iterator[Dict[str, BarData]]:
        """每次 yield 一个 {code: BarData} dict 表示同一交易日所有股票的 bar"""
        raise NotImplementedError


class DataFrameFeed(DataFeed):
    """从 pandas DataFrame 喂数据。

    DataFrame 列要求: code, date, open, high, low, close, volume[, amount, pre_close, is_suspended]
    """

    def __init__(self, df):
        import pandas as pd
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"]).dt.date
        if "pre_close" not in df.columns:
            df = df.sort_values(["code", "date"])
            df["pre_close"] = df.groupby("code")["close"].shift(1).fillna(df["close"])
        if "is_suspended" not in df.columns:
            df["is_suspended"] = df["volume"] == 0
        if "amount" not in df.columns:
            df["amount"] = df["close"] * df["volume"]
        self._df = df.sort_values(["date", "code"])

    def __iter__(self) -> Iterator[Dict[str, BarData]]:
        for d, group in self._df.groupby("date"):
            bars: Dict[str, BarData] = {}
            for row in group.itertuples(index=False):
                bars[row.code] = BarData(
                    code=row.code, dt=d,
                    open=float(row.open), high=float(row.high),
                    low=float(row.low), close=float(row.close),
                    volume=float(row.volume), amount=float(row.amount),
                    pre_close=float(row.pre_close),
                    is_suspended=bool(row.is_suspended),
                )
            yield bars


class CSVFeed(DataFeed):
    """从 CSV 喂数据。列同 DataFrameFeed。"""

    def __init__(self, path: str | Path):
        import pandas as pd
        self._df_feed = DataFrameFeed(pd.read_csv(path))

    def __iter__(self):
        return iter(self._df_feed)
