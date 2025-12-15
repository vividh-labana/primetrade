# 🚀 PrimeTrade - Binance Futures Trading Bot

A simplified trading bot for Binance Futures Testnet (USDT-M) built with Python.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **Market Orders**: Execute instant buy/sell orders at current market price
- **Limit Orders**: Place orders at specific price levels
- **Stop-Limit Orders**: Conditional orders with trigger and execution prices
- **OCO Orders**: One-Cancels-Other orders (Take-Profit + Stop-Loss)
- **Position Management**: View and manage open positions
- **Order Management**: View, track, and cancel orders
- **Interactive CLI**: User-friendly command-line interface
- **Comprehensive Logging**: Detailed logging of all API interactions
- **Input Validation**: Robust validation of all order parameters

## 📋 Prerequisites

- Python 3.8 or higher
- Binance Futures Testnet account
- API credentials from testnet

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd primetrade
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API credentials:**
   
   Create a `.env` file in the project root:
   ```env
   BINANCE_API_KEY=your_testnet_api_key
   BINANCE_API_SECRET=your_testnet_api_secret
   ```

## 🔑 Getting Testnet API Credentials

1. Go to [Binance Futures Testnet](https://testnet.binancefuture.com/)
2. Log in with your GitHub account
3. Navigate to API Management
4. Generate new API keys
5. Copy the API Key and Secret to your `.env` file

## 🚀 Usage

### Interactive Mode

Run the bot without any arguments to enter interactive mode:

```bash
python cli.py
```

Available commands in interactive mode:
- `help` - Show available commands
- `market` - Place a market order
- `limit` - Place a limit order
- `stop` - Place a stop-limit order
- `oco` - Place an OCO order
- `positions` - View current positions
- `orders` - View open orders
- `cancel` - Cancel a specific order
- `cancelall` - Cancel all orders for a symbol
- `account` - View account information
- `price` - Get current price for a symbol
- `leverage` - Set leverage for a symbol
- `quit` - Exit the bot

### Command-Line Mode

Execute single commands directly:

```bash
# Place a market buy order
python cli.py market -s BTCUSDT --side BUY -q 0.001

# Place a limit sell order
python cli.py limit -s BTCUSDT --side SELL -q 0.001 -p 100000

# Place a stop-limit order
python cli.py stop -s BTCUSDT --side SELL -q 0.001 -p 90000 --stop-price 91000

# View positions
python cli.py positions

# View open orders
python cli.py orders -s BTCUSDT

# Cancel an order
python cli.py cancel -s BTCUSDT --order-id 123456789

# View account info
python cli.py account
```

### Using as a Library

```python
from bot import BasicBot

# Initialize the bot
bot = BasicBot(
    api_key="your_api_key",
    api_secret="your_api_secret",
    testnet=True
)

# Place a market order
order = bot.place_market_order("BTCUSDT", "BUY", 0.001)

# Place a limit order
order = bot.place_limit_order("BTCUSDT", "SELL", 0.001, 100000)

# Place a stop-limit order
order = bot.place_stop_limit_order(
    symbol="BTCUSDT",
    side="SELL",
    quantity=0.001,
    price=90000,
    stop_price=91000
)

# Get positions
positions = bot.get_positions()

# Get open orders
orders = bot.get_open_orders("BTCUSDT")

# Cancel an order
bot.cancel_order("BTCUSDT", order_id=123456)
```

## 📁 Project Structure

```
primetrade/
├── bot.py              # Main trading bot class
├── cli.py              # Command-line interface
├── config.py           # Configuration management
├── logger.py           # Logging utilities
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore file
├── .env                # API credentials (create this)
└── README.md           # This file
```

## 📝 Order Types Explained

### Market Order
Executes immediately at the best available price.
```
Market BUY: Buy at current market price
Market SELL: Sell at current market price
```

### Limit Order
Executes only when the market reaches your specified price.
```
Limit BUY: Executes when price drops to your level
Limit SELL: Executes when price rises to your level
```

### Stop-Limit Order
A two-price order that triggers when the stop price is reached.
```
Stop Price: The trigger price that activates the order
Limit Price: The execution price once triggered
```

### OCO Order (One-Cancels-Other)
Combines take-profit and stop-loss orders. When one executes, the other is cancelled.
```
Take-Profit: Closes position at profit target
Stop-Loss: Closes position to limit losses
```

## ⚠️ Important Notes

- **TESTNET ONLY**: This bot is configured for Binance Futures Testnet
- **No Real Money**: Testnet uses virtual funds, not real cryptocurrency
- **API Rate Limits**: Be mindful of Binance API rate limits
- **Not Financial Advice**: This is an educational project

## 🔒 Security

- Never commit your `.env` file or API credentials
- Keep your API keys secure
- Use IP restrictions if available on Binance

## 📊 Logging

Logs are saved to the `logs/` directory with timestamps. Each session creates a new log file:
```
logs/trading_bot_20241215_143022.log
```

## 🛠️ Troubleshooting

### "Invalid API Key"
- Ensure you're using Testnet API keys, not mainnet
- Check that API keys are correctly copied without extra spaces

### "Order quantity too small"
- Check the minimum order quantity for the trading pair
- BTC minimum is typically 0.001

### "Insufficient balance"
- Request more testnet funds from the Binance Futures Testnet faucet

## 📜 License

MIT License - Feel free to use and modify for your projects.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

