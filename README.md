# mx-backtest

A 股事件驱动回测引擎。

## 特性

- T+1 持仓约束（今日买，次日才能卖）
- 涨跌停板限制（涨停不可买，跌停不可卖）
- 停牌检测（无成交量则跳过）
- 前复权 / 后复权
- 手续费 + 印花税 + 过户费
- 滑点模型（固定 / 比例 / 成交量加权）
- 事件驱动 Engine + 向量化 Backtest 双模式

## 安装

```bash
pip install mx-backtest
```

## 快速开始

```python
from mx_backtest import BacktestEngine

engine = BacktestEngine(initial_cash=100000)
result = engine.run(strategy, data)
print(result.summary())
```

## 项目结构

```
src/mx_backtest/
  __init__.py    # 包入口
  data.py        # 数据层 (BarData, DataFeed)
  portfolio.py   # 投资组合 (Portfolio, Position)
  costs.py       # 费用模型
  slippage.py    # 滑点模型
tests/
examples/
```
