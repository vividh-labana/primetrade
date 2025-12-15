#!/usr/bin/env python3
"""
Example: Basic usage of the PrimeTrade trading bot.

This script demonstrates how to use the BasicBot class
to interact with Binance Futures Testnet.

Before running:
1. Set up your API credentials in .env file
2. Ensure you have testnet funds
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import BasicBot
from display import Display


def main():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        Display.error("Please set BINANCE_API_KEY and BINANCE_API_SECRET in .env file")
        return
    
    # Initialize the bot
    Display.header()
    Display.info("Initializing trading bot...")
    
    try:
        bot = BasicBot(api_key, api_secret, testnet=True)
        Display.success("Bot initialized successfully!")
    except Exception as e:
        Display.error(f"Failed to initialize bot: {e}")
        return
    
    # Example 1: Get account info
    Display.separator()
    Display.info("Fetching account information...")
    try:
        account = bot.get_account_info()
        Display.account_info(account)
    except Exception as e:
        Display.error(f"Error: {e}")
    
    # Example 2: Get current BTC price
    Display.separator()
    Display.info("Fetching BTCUSDT price...")
    try:
        price = bot.get_symbol_price("BTCUSDT")
        Display.price("BTCUSDT", price)
    except Exception as e:
        Display.error(f"Error: {e}")
    
    # Example 3: Check positions
    Display.separator()
    Display.info("Checking current positions...")
    try:
        positions = bot.get_positions()
        Display.positions(positions)
    except Exception as e:
        Display.error(f"Error: {e}")
    
    # Example 4: Check open orders
    Display.separator()
    Display.info("Checking open orders...")
    try:
        orders = bot.get_open_orders()
        Display.open_orders(orders)
    except Exception as e:
        Display.error(f"Error: {e}")
    
    # Example 5: Place a small limit order (won't execute immediately)
    Display.separator()
    Display.info("Placing a test limit order...")
    
    try:
        # Get current price
        current_price = bot.get_symbol_price("BTCUSDT")
        
        # Place a limit buy order 10% below current price (won't fill)
        test_price = current_price * 0.9
        
        order = bot.place_limit_order(
            symbol="BTCUSDT",
            side="BUY",
            quantity=0.001,  # Minimum quantity
            price=test_price
        )
        
        Display.order_result(order, "Test Limit Order")
        Display.success("Test order placed!")
        
        # Cancel the test order
        Display.info("Cancelling test order...")
        bot.cancel_order("BTCUSDT", order['orderId'])
        Display.success("Test order cancelled!")
        
    except Exception as e:
        Display.error(f"Error placing test order: {e}")
    
    Display.separator()
    Display.success("Example completed successfully!")
    Display.info("Check the logs/ directory for detailed logs.")


if __name__ == '__main__':
    main()

