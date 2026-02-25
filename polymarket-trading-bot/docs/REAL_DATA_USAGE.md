# 使用真实历史数据进行回测

## 概述

现在回测系统支持两种数据源:
1. **模拟数据** (默认) - 基于随机游走算法生成的模拟市场数据
2. **真实数据** - 从Polymarket API获取的实际历史交易数据

## 安装依赖

使用真实数据前,确保已安装必要的依赖:

```bash
pip install py-clob-client
```

## 快速开始

### 1. 查看可用市场

首先,列出Polymarket上的热门市场:

```bash
python scripts/list_markets.py
```

输出示例:
```
📊 Polymarket热门市场
============================================================
1. Will Donald Trump win the 2024 US Presidential Election?
   Market ID: 0x1234567890abcdef...
   流动性: $5,234,123 | 成交量: $45,678,901

2. Will the Federal Reserve cut rates in March 2024?
   Market ID: 0xabcdef1234567890...
   流动性: $2,345,678 | 成交量: $12,345,678
...
```

### 2. 搜索特定市场

使用关键词搜索市场:

```bash
python scripts/list_markets.py --search "Trump"
python scripts/list_markets.py --search "Election"
python scripts/list_markets.py --search "Bitcoin"
```

### 3. 运行真实数据回测

使用 `--real` 参数启用真实数据:

```bash
# 使用关键词搜索市场
python scripts/run_backtest.py --market "Trump" --real

# 指定时间范围
python scripts/run_backtest.py --market "Trump" --start 2024-01-01 --end 2024-11-05 --real

# 使用完整的Market ID
python scripts/run_backtest.py --market "0x1234567890abcdef..." --real
```

### 4. 对比模拟数据和真实数据

```bash
# 模拟数据回测 (默认)
python scripts/run_backtest.py --market "Trump"

# 真实数据回测
python scripts/run_backtest.py --market "Trump" --real
```

## 命令行参数

### run_backtest.py

```bash
python scripts/run_backtest.py [参数]

参数:
  --start DATE      开始日期 (格式: YYYY-MM-DD, 默认: 2024-01-01)
  --end DATE        结束日期 (格式: YYYY-MM-DD, 默认: 2024-11-05)
  --market KEYWORD  市场ID或搜索关键词 (默认: trump)
  --real           使用真实数据而非模拟数据
```

### list_markets.py

```bash
python scripts/list_markets.py [参数]

参数:
  --search KEYWORD  搜索包含关键词的市场
```

## 数据源说明

### 模拟数据特征
- **生成方式**: 随机游走算法 + 15%套利机会概率
- **优点**:
  - 无需联网
  - 数据量可控
  - 快速测试
- **缺点**:
  - 不反映真实市场行为
  - 套利机会过于理想化
  - 结果仅供参考

### 真实数据特征
- **数据源**: Polymarket CLOB API
- **包含内容**:
  - 实际交易历史
  - 真实价格变动
  - 实际流动性数据
- **优点**:
  - 反映真实市场条件
  - 更准确的回测结果
  - 可验证策略有效性
- **限制**:
  - 需要网络连接
  - API可能有速率限制
  - 历史数据可能不完整

## API限制说明

Polymarket CLOB API有以下限制:
- **速率限制**: 建议控制请求频率
- **数据范围**: 部分老旧市场可能数据不全
- **历史深度**: API提供的历史数据深度有限

如遇到速率限制,程序会自动回退到模拟数据。

## 代码示例

### 在代码中使用真实数据

```python
from src.backtesting.backtest_engine import BacktestEngine

# 初始化回测引擎 (使用真实数据)
engine = BacktestEngine(use_real_data=True)

# 加载数据
market_data = engine.load_historical_data(
    market_id="Trump",  # 可以是关键词或完整Market ID
    start_date="2024-01-01",
    end_date="2024-11-05"
)

# 运行回测
results = await engine.run_backtest(market_data)
engine.print_results(results)
```

### 直接使用数据加载器

```python
from src.data.historical_loader import HistoricalDataLoader

loader = HistoricalDataLoader()

# 搜索市场
market = loader.get_market_by_name("Trump")
print(f"Market ID: {market['condition_id']}")

# 加载交易历史
trades_df = loader.load_trade_history(
    market_id=market['condition_id'],
    start_date="2024-01-01",
    end_date="2024-11-05"
)

# 加载价格快照
prices_df = loader.load_orderbook_snapshots(
    market_id=market['condition_id'],
    start_date="2024-01-01",
    end_date="2024-11-05",
    interval_hours=1  # 每小时采样
)
```

## 常见问题

### Q: 为什么没有获取到真实数据?

**A**: 可能的原因:
1. 未安装 `py-clob-client` - 运行 `pip install py-clob-client`
2. 网络连接问题 - 检查网络是否正常
3. Market ID错误 - 使用 `list_markets.py` 查找正确的ID
4. API速率限制 - 稍后重试

程序会在无法获取真实数据时自动回退到模拟数据。

### Q: 真实数据回测结果与模拟数据差异很大?

**A**: 这是正常的,原因:
- 真实市场中套利机会较少(<5%)
- 实际价差通常更小
- 流动性和滑点影响更明显
- 真实数据更能反映策略的实际表现

### Q: 如何找到特定事件的Market ID?

**A**: 三种方法:
1. 使用 `list_markets.py` 浏览热门市场
2. 使用 `list_markets.py --search "关键词"` 搜索
3. 直接在 Polymarket 网站上找到市场页面,URL中包含Market ID

### Q: 历史数据能追溯到多久以前?

**A**:
- Polymarket API提供的历史数据深度因市场而异
- 一般可获取到市场创建以来的所有交易
- 部分老旧或低流动性市场数据可能不完整

## 性能对比示例

### 模拟数据回测结果
```
初始资金:     $10,000.00
最终资金:     $33,054.67
总收益:       $23,054.67
收益率:       230.55%
总交易次数:   462
胜率:         100.00%
```

### 真实数据回测结果 (示例)
```
初始资金:     $10,000.00
最终资金:     $10,234.56
总收益:       $234.56
收益率:       2.35%
总交易次数:   23
胜率:         87.00%
```

**结论**: 真实市场中套利机会更少,收益更低,但结果更可靠。

## 最佳实践

1. **先用模拟数据快速验证策略逻辑**
2. **再用真实数据验证实际表现**
3. **对比多个不同市场的回测结果**
4. **注意API速率限制,避免频繁请求**
5. **定期更新历史数据以反映最新市场条件**

## 下一步

- 使用真实数据验证策略有效性
- 根据回测结果调整策略参数 ([config/strategies.yaml](../config/strategies.yaml))
- 在模拟交易模式下测试 (`python src/main.py --dry-run`)
- 谨慎开始小额实盘交易
