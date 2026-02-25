# Polymarket自动交易程序 - 快速入门指南

## 📋 前置要求

1. **Python 3.9+** - 确保已安装
2. **Polymarket账户** - 用于API访问
3. **以太坊钱包** - 用于链上交易(Polygon网络)
4. **基本的Python和命令行知识**

## 🚀 5分钟快速启动

### 步骤1: 克隆/下载项目

如果你还没有项目代码:

```bash
# 进入项目目录
cd polymarket-trading-bot
```

### 步骤2: 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 步骤3: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件 (使用你喜欢的编辑器)
# macOS/Linux:
nano .env
# 或者
vim .env

# Windows:
notepad .env
```

**最小配置** (用于测试):

```bash
# .env文件内容
POLYMARKET_API_KEY=your_key_here
POLYMARKET_API_SECRET=your_secret_here
ETH_PRIVATE_KEY=your_private_key_here
ETH_RPC_URL=https://polygon-rpc.com

DRY_RUN=true
TRADING_ENABLED=false
LOG_LEVEL=INFO
```

### 步骤4: 初始化数据库

```bash
python scripts/setup_database.py
```

### 步骤5: 运行程序(模拟模式)

```bash
# 模拟交易模式 - 安全测试
python src/main.py --dry-run
```

你应该看到类似这样的输出:

```
2024-02-25 15:30:00 | INFO     | __main__:main:45 - ============================================================
2024-02-25 15:30:00 | INFO     | __main__:main:46 - Polymarket自动交易程序启动
2024-02-25 15:30:00 | INFO     | __main__:main:47 - ============================================================
2024-02-25 15:30:00 | INFO     | __main__:main:48 - 环境: development
2024-02-25 15:30:00 | INFO     | __main__:main:49 - 模拟交易模式: True
2024-02-25 15:30:00 | INFO     | __main__:main:50 - 自动交易: 禁用
2024-02-25 15:30:00 | WARNING  | __main__:main:54 - ⚠️  当前运行在模拟交易模式,不会执行实际交易
```

## 📝 下一步

### 配置风险参数

编辑 `config/risk_params.yaml`:

```yaml
max_position_size: 100      # 从小金额开始
max_total_exposure: 500     # 总敞口
daily_loss_limit: 50        # 每日最大亏损
```

### 配置策略参数

编辑 `config/strategies.yaml`:

```yaml
arbitrage:
  min_spread: 0.02          # 最小2%价差
  min_profit: 5             # 最小$5利润
  fee_rate: 0.001           # 0.1%手续费
```

### 查看日志

```bash
# 实时查看交易日志
tail -f logs/trading_$(date +%Y-%m-%d).log

# 查看错误日志
tail -f logs/errors_$(date +%Y-%m-%d).log
```

## ⚠️ 重要提示

### 在启用实盘交易前:

1. **充分测试模拟模式** - 至少运行24小时
2. **理解风险参数** - 确保你理解每个配置项的含义
3. **从小金额开始** - 初始投入不超过你愿意损失的金额
4. **监控日志** - 定期检查程序运行状态
5. **备份私钥** - 确保私钥安全保存

### 启用实盘交易:

编辑 `config/config.yaml`:

```yaml
trading:
  enabled: true           # 启用交易
  dry_run: false          # 关闭模拟模式
```

然后运行:

```bash
python src/main.py
```

## 🛠️ 常见问题解决

### 问题1: 导入错误

```bash
# 确保在项目根目录
cd polymarket-trading-bot

# 确保虚拟环境已激活
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 重新安装依赖
pip install -r requirements.txt
```

### 问题2: 配置文件找不到

```bash
# 确保配置文件存在
ls config/

# 应该看到:
# config.yaml  risk_params.yaml  strategies.yaml
```

### 问题3: 数据库错误

```bash
# 删除旧数据库并重新初始化
rm -f data/polymarket.db
python scripts/setup_database.py
```

### 问题4: API连接失败

- 检查 `.env` 文件中的API密钥是否正确
- 确认网络连接正常
- 查看 `logs/errors_*.log` 了解详细错误

## 📚 进阶使用

### 运行回测

```bash
# 回测2024年全年数据
python scripts/run_backtest.py --start 2024-01-01 --end 2024-12-31

# 回测特定策略
python scripts/run_backtest.py --strategy arbitrage
```

### 自定义策略

1. 在 `src/strategies/` 创建新策略文件
2. 继承 `BaseStrategy` 类
3. 在 `config/strategies.yaml` 添加配置

### 监控和告警

在 `.env` 中配置Telegram或Slack:

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Slack
SLACK_WEBHOOK_URL=your_webhook_url
```

## 🆘 获取帮助

- **文档**: 查看 `docs/` 目录
- **配置说明**: 参考 `config/*.yaml` 文件中的注释
- **完整README**: 查看根目录的 `README.md`

## 🎯 性能优化建议

1. **调整更新间隔**: 在 `config/config.yaml` 中设置 `update_interval`
2. **限制监控市场**: 在 `config/config.yaml` 的 `markets` 数组中指定特定市场
3. **使用PostgreSQL**: 对于大量数据,切换到PostgreSQL数据库

## 🔒 安全检查清单

- [ ] 私钥已安全存储,未提交到Git
- [ ] `.env` 文件在 `.gitignore` 中
- [ ] 风险参数设置合理
- [ ] 已充分测试模拟模式
- [ ] 启用了熔断器
- [ ] 配置了每日损失上限
- [ ] 定期备份数据和配置

---

**祝你交易顺利!记得风险管理第一!** 🎊
