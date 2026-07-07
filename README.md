# mx-backtest

> 🇨🇳 A 股事件驱动回测引擎 — T+1 / 涨跌停 / 停牌 / 复权 / 手续费 / 滑点

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/27dream/mx-backtest?style=social)](https://github.com/27dream/mx-backtest)
[![PyPI](https://img.shields.io/pypi/v/mx-backtest)](https://pypi.org/project/mx-backtest/)

专为中国 A 股市场设计的量化回测框架，与 **mx-trader-bridge**（自动交易桥接层）和 **mcp-eastmoney**（实时行情）形成完整量化链路。

---

## 特性

### 已实现（v0.1.0）

| 特性 | 说明 |
|------|------|
| ✅ **T+1 持仓约束** | 当日买入的股票次日才可卖出，精确追踪 A 股交收规则 |
| ✅ **涨跌停板** | 涨停不可买入、跌停不可卖出；检测一字板/封板状态 |
| ✅ **停牌检测** | 成交量为 0 自动判定为停牌，跳过该日交易 |
| ✅ **A 股费用模型** | 佣金（万 2.5，最低 5 元）、印花税（0.05% 卖方）、过户费（0.001% 双边） |
| ✅ **滑点模型** | 固定 tick 滑点 / 百分比滑点（默认万 5），均可自定义 |
| ✅ **前复权数据** | BarData 默认使用前复权价格 |
| ✅ **数据接入** | Pandas DataFrame / CSV 双模式 DataFeed |
| ✅ **持仓管理** | 持仓均价、可卖数量、实时盈亏追踪 |

### 规划中

| 特性 | 状态 |
|------|:----:|
| 🚧 事件驱动 Engine | 架构设计中 |
| 🚧 Broker（订单路由 + 撮合） | 架构设计中 |
| 🚧 Strategy 基类 | 架构设计中 |
| 🚧 绩效指标（夏普/最大回撤/胜率） | 架构设计中 |
| 🚧 多标的组合回测 | 规划中 |
| 🚧 参数优化器 | 规划中 |

---

## 安装

```bash
pip install mx-backtest
```

或从源码安装：

```bash
git clone https://github.com/27dream/mx-backtest.git
cd mx-backtest
pip install -e .
```

---

## 快速开始

### 准备数据

```python
import pandas as pd
from mx_backtest import DataFrameFeed

# 从 DataFrame 创建数据源
df = pd.read_csv("000001.csv")  # 平安银行日线数据
feed = DataFrameFeed(df)

# 或从 CSV 直接读取
from mx_backtest import CSVFeed
feed = CSVFeed("data/000001.csv")
```

### 配置费用和滑点

```python
from mx_backtest import AShareCostModel, PercentSlippage

# A 股标准费率（可按账户实际调整）
cost_model = AShareCostModel(
    commission_rate=0.00025,  # 万 2.5
    stamp_tax=0.0005,         # 印花税 0.05%
    transfer_fee=0.00001,     # 过户费
)

# 万 5 比例滑点
slippage = PercentSlippage(pct=0.0005)
```

### 遍历 K 线

```python
from mx_backtest import Portfolio

portfolio = Portfolio(cash=100_000)  # 10 万初始资金

for day_bars in feed:
    # day_bars: Dict[str, BarData] — 当日所有股票行情
    
    for code, bar in day_bars.items():
        # 更新持仓市价
        portfolio.update_market_prices({code: bar.close})
        
        # 检查涨跌停状态
        if bar.is_limit_up:
            print(f"{code} 涨停了，不可买入")
        if bar.is_limit_down:
            print(f"{code} 跌停了，不可卖出")
        if bar.is_suspended:
            print(f"{code} 今日停牌")
    
    # T+1 解冻：新交易日开盘前将持仓转为可卖
    portfolio.on_new_day()
```

---

## 项目结构

```
mx-backtest/
├── src/
│   └── mx_backtest/
│       ├── __init__.py    # 包入口 & 公开 API
│       ├── data.py        # BarData / DataFeed / CSVFeed / DataFrameFeed
│       ├── portfolio.py   # Portfolio / Position（含 T+1 可卖逻辑）
│       ├── costs.py       # CostModel / AShareCostModel
│       └── slippage.py    # Slippage / FixedSlippage / PercentSlippage
├── tests/                 # 测试用例（coming soon）
├── examples/              # 使用示例（coming soon）
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## API 参考

### `BarData`

单根 K 线数据类，默认使用前复权价格。

| 属性 | 类型 | 说明 |
|------|------|------|
| `code` | `str` | 股票代码 |
| `dt` | `date` | 交易日 |
| `open / high / low / close` | `float` | 价格 |
| `volume` | `float` | 成交量 |
| `amount` | `float` | 成交额 |
| `pre_close` | `float` | 昨收价 |
| `is_suspended` | `bool` | 是否停牌 |

| 方法/属性 | 返回 | 说明 |
|-----------|------|------|
| `.limit_up` | `float` | 涨停价（默认 10%） |
| `.limit_down` | `float` | 跌停价 |
| `.is_limit_up` | `bool` | 是否封涨停 |
| `.is_limit_down` | `bool` | 是否封跌停 |

### `AShareCostModel`

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `commission_rate` | `0.00025` | 佣金费率（万 2.5） |
| `min_commission` | `5.0` | 最低佣金（元） |
| `stamp_tax` | `0.0005` | 印花税率（卖方） |
| `transfer_fee` | `0.00001` | 过户费率 |

### `Position`

| 属性 | 说明 |
|------|------|
| `qty` | 总持仓数量 |
| `avail_qty` | 可卖数量（T+1 冻结当日买入） |
| `avg_cost` | 持仓均价 |
| `last_price` | 最新价 |
| `market_value` | 持仓市值 |
| `pnl` | 浮动盈亏 |

---

## 生态

```
mcp-eastmoney ──►  mx-backtest ──►  mx-trader-bridge ──►  mx-risk-guard
  实时行情             回测验证           自动交易              风控引擎
```

- [mcp-eastmoney](https://github.com/27dream/mcp-eastmoney) — 基于 MCP 协议的 A 股实时行情接口
- [mx-trader-bridge](https://github.com/27dream/mx-trader-bridge) — AI 决策到东方财富妙想模拟盘的自动交易桥接层
- [mx-risk-guard](https://github.com/27dream/mx-risk-guard) — A 股交易风控引擎

---

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feat/your-feature`
3. 提交改动: `git commit -m 'Add some feature'`
4. 推送到分支: `git push origin feat/your-feature`
5. 提交 Pull Request

### 开发环境

```bash
pip install -e ".[dev]"
pytest tests/
```

---

## License

[MIT](LICENSE) © 2026 27dream
