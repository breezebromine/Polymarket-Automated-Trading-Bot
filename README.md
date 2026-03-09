# Polymarket Automated Trading Bot

A Python-based Polymarket automated trading system that supports market data monitoring, automated arbitrage trading strategies, risk management, and backtesting capabilities.

## Features

- **Market Data Monitoring**: Real-time collection of Polymarket market prices, order book, and trade data
- **Arbitrage Strategies**: Automatically identify and execute arbitrage opportunities
  - YES/NO price imbalance arbitrage
  - Cross-market spread arbitrage
- **Risk Management**: Comprehensive risk control mechanisms
  - Position limits and total exposure management
  - Daily loss limits
  - Circuit breaker (automatic shutdown on anomalies)
- **Backtesting System**: Validate strategy effectiveness using historical data
  - Support for simulated data for quick testing
  - Support for real Polymarket historical data
- **Logging & Monitoring**: Detailed trading logs and performance monitoring

## Tech Stack

- **Language**: Python 3.9+
- **API**: py-clob-client (Polymarket official client)
- **Web3**: web3.py (Ethereum/Polygon blockchain interaction)
- **Database**: SQLite/PostgreSQL + SQLAlchemy
- **Async**: asyncio + aiohttp
- **Logging**: loguru
- **Data Analysis**: pandas + numpy

## Project Structure

```
polymarket-trading-bot/
├── src/                    # Source code
│   ├── api/               # API clients
│   ├── data/              # Data collection and storage
│   ├── strategies/        # Trading strategies
│   ├── trading/           # Trade execution
│   ├── risk/              # Risk management
│   ├── backtesting/       # Backtesting system
│   ├── monitoring/        # Monitoring and logging
│   └── utils/             # Utility modules
├── config/                # Configuration files
├── data/                  # Data directory
├── logs/                  # Logs directory
├── scripts/               # Script tools
├── tests/                 # Tests
└── docs/                  # Documentation
```

## Quick Start

### 1. Environment Setup

Ensure Python 3.9 or higher is installed:

```bash
python --version
```

### 2. Install Dependencies

```bash
cd polymarket-trading-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy environment variable template
cp .env.example .env

# Edit the .env file and fill in your API keys and private key
# ⚠️ Warning: Keep your private key safe, do not leak or commit it to version control
```

Required environment variables:

- `POLYMARKET_API_KEY`: Polymarket API key
- `POLYMARKET_API_SECRET`: Polymarket API secret
- `ETH_PRIVATE_KEY`: Ethereum wallet private key
- `ETH_RPC_URL`: Polygon RPC URL

### 4. Initialize Database

```bash
python scripts/setup_database.py
```

### 5. Run the Program

**Simulated Trading Mode (recommended for first-time use)**:

```bash
python src/main.py --dry-run
```

**Live Trading Mode** (use with caution, thorough testing recommended first):

```bash
# Ensure reasonable risk parameters are set in config/config.yaml
python src/main.py
```

## Configuration

### Main Configuration File (config/config.yaml)

```yaml
system:
  environment: development  # Environment: development, staging, production
  debug: true              # Enable debug mode
  log_level: INFO          # Log level

trading:
  enabled: false           # Enable automated trading
  dry_run: true           # Simulated trading mode
  update_interval: 5      # Data update interval (seconds)
```

### Risk Parameters (config/risk_params.yaml)

```yaml
max_position_size: 1000      # Maximum position per market (USD)
max_total_exposure: 5000     # Total exposure limit (USD)
daily_loss_limit: 500        # Maximum daily loss (USD)
min_liquidity: 1000          # Minimum market liquidity requirement (USD)
```

### Strategy Configuration (config/strategies.yaml)

```yaml
arbitrage:
  min_spread: 0.02           # Minimum spread (2%)
  min_profit: 5              # Minimum expected profit (USD)
  fee_rate: 0.001            # Fee rate (0.1%)
  slippage_tolerance: 0.005  # Slippage tolerance (0.5%)
```

## Security Notes

### 🔒 Private Key Security

1. **Never** commit private keys to Git repositories
2. **Never** hardcode private keys in code
3. Use environment variables to store sensitive information
4. Consider using hardware wallets or key management services

### 💰 Fund Security

1. **Start Small**: Use lower position limits for initial testing
2. **Use Simulation Mode**: Thoroughly test before switching to live trading
3. **Set Stop Loss**: Configure reasonable daily loss limits
4. **Monitor Logs**: Regularly check trading logs and stop immediately if anomalies are detected

### 🛡️ Risk Control

1. Set risk parameters in configuration files according to your risk tolerance
2. Enable circuit breakers to prevent consecutive losses
3. Regularly review trading performance
4. Maintain sufficient liquidity reserves

## Backtesting

### Backtest with Simulated Data

Run historical data backtest (using simulated data):

```bash
python scripts/run_backtest.py --start 2024-01-01 --end 2024-12-31
```

### Backtest with Real Data

First, view available markets:

```bash
# List popular markets
python scripts/list_markets.py

# Search for specific markets
python scripts/list_markets.py --search "Trump"
```

Run backtest with real data:

```bash
# Use real Polymarket data
python scripts/run_backtest.py --market "Trump" --real

# Specify date range
python scripts/run_backtest.py --market "Election" --start 2024-01-01 --end 2024-11-05 --real
```

**Detailed Instructions**: See [Real Data Usage Guide](docs/REAL_DATA_USAGE.md)

Backtest results will be saved in the `data/backtest/` directory.

## Development Guide

### Adding New Strategies

1. Create a new strategy file in the `src/strategies/` directory
2. Inherit from the `BaseStrategy` base class
3. Implement required methods: `generate_signals()`, `on_market_data()`, etc.
4. Add strategy configuration in `config/strategies.yaml`

Example:

```python
from .base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def generate_signals(self, market_data):
        # Implement your strategy logic
        pass
```

### Run Tests

```bash
pytest tests/
```

## Monitoring and Logging

Log file locations:
- `logs/trading_YYYY-MM-DD.log`: Trading logs
- `logs/errors_YYYY-MM-DD.log`: Error logs
- `logs/debug_YYYY-MM-DD.log`: Debug logs (debug mode only)

View logs in real-time:

```bash
tail -f logs/trading_$(date +%Y-%m-%d).log
```

## FAQ

### Q: How to obtain Polymarket API keys?

A: Visit [Polymarket Documentation](https://docs.polymarket.com/) to register and obtain API keys.

### Q: How much initial capital is needed?

A: At least $100-500 is recommended for testing, adjust based on configured risk parameters.

### Q: What is the expected return rate for arbitrage strategies?

A: Depends on market conditions. Arbitrage opportunities are typically rare but lower risk. Evaluate through backtesting.

### Q: How to stop the program?

A: Use `Ctrl+C` for graceful shutdown, or run the emergency stop script:

```bash
python scripts/emergency_stop.py
```

## Disclaimer

⚠️ **Risk Warning**:

- This software is for educational and research purposes only
- Cryptocurrency and prediction market trading involves high risk
- May result in partial or total loss of capital
- All risks from using this software for trading are borne by the user
- The author is not responsible for any trading losses

**Please use with caution and full understanding of the risks**

## Contributing

Issues and Pull Requests are welcome!

## License

MIT License

## Contact

- Issues: [GitHub Issues](https://github.com/yourname/polymarket-trading-bot/issues)
- Documentation: [Full Documentation](./docs/)
- For Higher Porofit Contact me
- Discord: [bromine0915](https://discord.gg/ZKBs6UkT)

## Acknowledgments

- [Polymarket](https://polymarket.com/) - Decentralized prediction market platform
- [py-clob-client](https://github.com/Polymarket/py-clob-client) - Polymarket official Python client

---

**Happy Trading!** 📈

Remember: Risk management always comes first.
