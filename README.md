# Binance Futures Trading Bot

A simplified trading bot for Binance Futures Testnet (USDT-M).

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Binance Testnet credentials:
```env
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

Get credentials from: https://testnet.binancefuture.com/

## Usage

### Interactive Mode
```bash
python main.py
```

### Command Line Mode
```bash
# Market order
python main.py market -s BTCUSDT --side BUY -q 0.001

# Limit order
python main.py limit -s BTCUSDT --side SELL -q 0.001 -p 100000

# Stop-limit order
python main.py stop -s BTCUSDT --side SELL -q 0.001 -p 90000 --stop-price 91000

# View positions
python main.py positions

# View orders
python main.py orders

# Cancel order
python main.py cancel -s BTCUSDT --order-id 123456
```

### As a Library
```python
from bot import BasicBot

bot = BasicBot(api_key, api_secret, testnet=True)

# Market order
bot.place_market_order("BTCUSDT", "BUY", 0.001)

# Limit order
bot.place_limit_order("BTCUSDT", "SELL", 0.001, 100000)

# Stop-limit order
bot.place_stop_limit_order("BTCUSDT", "SELL", 0.001, 90000, 91000)

# OCO order
bot.place_oco_order("BTCUSDT", "SELL", 0.001, 110000, 95000, 94500)
```

## Features

- Market and Limit orders
- Stop-Limit orders (bonus)
- OCO orders (bonus)
- Input validation
- Logging (console + file)
- Error handling

## Project Structure

```
├── bot.py          # Trading bot class
├── cli.py          # CLI interface
├── main.py         # Entry point
├── config.py       # Configuration
├── logger.py       # Logging
├── validators.py   # Input validation
└── display.py      # Output formatting
```
