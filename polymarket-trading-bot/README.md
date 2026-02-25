# Polymarket自动交易程序

一个基于Python的Polymarket自动交易系统,支持市场数据监控、自动套利交易策略、风险管理和回测功能。

## 功能特性

- **市场数据监控**: 实时采集Polymarket市场价格、订单簿和成交数据
- **套利策略**: 自动识别和执行套利机会
  - YES/NO价格不平衡套利
  - 跨市场价差套利
- **风险管理**: 完善的风险控制机制
  - 仓位限制和总敞口管理
  - 每日损失上限
  - 熔断器(异常自动停止)
- **回测系统**: 使用历史数据验证策略有效性
  - 支持模拟数据快速测试
  - 支持真实Polymarket历史数据
- **日志监控**: 详细的交易日志和性能监控

## 技术栈

- **语言**: Python 3.9+
- **API**: py-clob-client (Polymarket官方客户端)
- **Web3**: web3.py (以太坊/Polygon链上交互)
- **数据库**: SQLite/PostgreSQL + SQLAlchemy
- **异步**: asyncio + aiohttp
- **日志**: loguru
- **数据分析**: pandas + numpy

## 项目结构

```
polymarket-trading-bot/
├── src/                    # 源代码
│   ├── api/               # API客户端
│   ├── data/              # 数据采集和存储
│   ├── strategies/        # 交易策略
│   ├── trading/           # 交易执行
│   ├── risk/              # 风险管理
│   ├── backtesting/       # 回测系统
│   ├── monitoring/        # 监控和日志
│   └── utils/             # 工具模块
├── config/                # 配置文件
├── data/                  # 数据目录
├── logs/                  # 日志目录
├── scripts/               # 脚本工具
├── tests/                 # 测试
└── docs/                  # 文档
```

## 快速开始

### 1. 环境准备

确保已安装Python 3.9或更高版本:

```bash
python --version
```

### 2. 安装依赖

```bash
cd polymarket-trading-bot

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\\Scripts\\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件,填入你的API密钥和私钥
# ⚠️ 警告: 请妥善保管私钥,不要泄露或提交到版本控制系统
```

需要配置的关键环境变量:

- `POLYMARKET_API_KEY`: Polymarket API密钥
- `POLYMARKET_API_SECRET`: Polymarket API密钥
- `ETH_PRIVATE_KEY`: 以太坊钱包私钥
- `ETH_RPC_URL`: Polygon RPC URL

### 4. 初始化数据库

```bash
python scripts/setup_database.py
```

### 5. 运行程序

**模拟交易模式(推荐首次使用)**:

```bash
python src/main.py --dry-run
```

**实盘交易模式** (请谨慎使用,建议先充分测试):

```bash
# 确保在config/config.yaml中设置了合理的风险参数
python src/main.py
```

## 配置说明

### 主配置文件 (config/config.yaml)

```yaml
system:
  environment: development  # 环境: development, staging, production
  debug: true              # 是否启用调试模式
  log_level: INFO          # 日志级别

trading:
  enabled: false           # 是否启用自动交易
  dry_run: true           # 模拟交易模式
  update_interval: 5      # 数据更新间隔(秒)
```

### 风险参数 (config/risk_params.yaml)

```yaml
max_position_size: 1000      # 单个市场最大头寸(USD)
max_total_exposure: 5000     # 总敞口限制(USD)
daily_loss_limit: 500        # 每日最大亏损(USD)
min_liquidity: 1000          # 最小市场流动性要求(USD)
```

### 策略配置 (config/strategies.yaml)

```yaml
arbitrage:
  min_spread: 0.02           # 最小价差(2%)
  min_profit: 5              # 最小预期利润(USD)
  fee_rate: 0.001            # 手续费率(0.1%)
  slippage_tolerance: 0.005  # 滑点容忍度(0.5%)
```

## 安全注意事项

### 🔒 私钥安全

1. **永远不要**将私钥提交到Git仓库
2. **永远不要**在代码中硬编码私钥
3. 使用环境变量存储敏感信息
4. 考虑使用硬件钱包或密钥管理服务

### 💰 资金安全

1. **从小额开始**: 初期使用较低的仓位限制进行测试
2. **使用模拟模式**: 充分测试后再切换到实盘
3. **设置止损**: 配置合理的每日损失上限
4. **监控日志**: 定期查看交易日志,发现异常及时停止

### 🛡️ 风险控制

1. 配置文件中的风险参数根据你的风险承受能力设置
2. 启用熔断器,防止连续亏损
3. 定期审查交易表现
4. 保持足够的流动性储备

## 回测

### 使用模拟数据回测

运行历史数据回测(使用模拟数据):

```bash
python scripts/run_backtest.py --start 2024-01-01 --end 2024-12-31
```

### 使用真实数据回测

首先查看可用的市场:

```bash
# 列出热门市场
python scripts/list_markets.py

# 搜索特定市场
python scripts/list_markets.py --search "Trump"
```

运行真实数据回测:

```bash
# 使用真实Polymarket数据
python scripts/run_backtest.py --market "Trump" --real

# 指定日期范围
python scripts/run_backtest.py --market "Election" --start 2024-01-01 --end 2024-11-05 --real
```

**详细说明**: 查看 [真实数据使用指南](docs/REAL_DATA_USAGE.md)

回测结果将保存在`data/backtest/`目录。

## 开发指南

### 添加新策略

1. 在`src/strategies/`目录创建新策略文件
2. 继承`BaseStrategy`基类
3. 实现必要的方法: `generate_signals()`, `on_market_data()`等
4. 在`config/strategies.yaml`中添加策略配置

示例:

```python
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def generate_signals(self, market_data):
        # 实现你的策略逻辑
        pass
```

### 运行测试

```bash
pytest tests/
```

## 监控和日志

日志文件位置:
- `logs/trading_YYYY-MM-DD.log`: 交易日志
- `logs/errors_YYYY-MM-DD.log`: 错误日志
- `logs/debug_YYYY-MM-DD.log`: 调试日志(仅在debug模式)

实时查看日志:

```bash
tail -f logs/trading_$(date +%Y-%m-%d).log
```

## 常见问题

### Q: 如何获取Polymarket API密钥?

A: 访问 [Polymarket文档](https://docs.polymarket.com/) 注册并获取API密钥。

### Q: 需要多少初始资金?

A: 建议至少$100-500用于测试,根据配置的风险参数调整。

### Q: 套利策略的预期收益率是多少?

A: 取决于市场条件,通常套利机会较少但风险较低。建议通过回测评估。

### Q: 如何停止程序?

A: 使用`Ctrl+C`优雅停止,或运行紧急停止脚本:

```bash
python scripts/emergency_stop.py
```

## 免责声明

⚠️ **风险提示**:

- 本软件仅供学习和研究使用
- 加密货币和预测市场交易存在高风险
- 可能导致部分或全部资金损失
- 使用本软件进行交易的所有风险由用户自行承担
- 作者不对任何交易损失负责

**请在充分理解风险的情况下谨慎使用**

## 贡献

欢迎提交Issue和Pull Request!

## 许可证

MIT License

## 联系方式

- Issues: [GitHub Issues](https://github.com/yourname/polymarket-trading-bot/issues)
- 文档: [完整文档](./docs/)

## 致谢

- [Polymarket](https://polymarket.com/) - 去中心化预测市场平台
- [py-clob-client](https://github.com/Polymarket/py-clob-client) - Polymarket官方Python客户端

---

**祝你交易顺利!** 📈

记得: 风险管理永远是第一位的。
