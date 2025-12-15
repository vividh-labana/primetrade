#!/usr/bin/env python3
"""
Example: Advanced order types with PrimeTrade.

This script demonstrates:
- Stop-Limit orders
- Take-Profit orders
- OCO (One-Cancels-Other) orders

Before running:
1. Set up your API credentials in .env file
2. Ensure you have an open position (for exit orders)
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot import BasicBot
from display import Display


def demonstrate_stop_limit(bot: BasicBot):
    """Demonstrate stop-limit order placement."""
    Display.info("=== Stop-Limit Order Example ===")
    
    try:
        current_price = bot.get_symbol_price("BTCUSDT")
        Display.price("BTCUSDT", current_price)
        
        # Stop-limit sell order: triggers at 95%, executes at 94.5%
        stop_price = current_price * 0.95
        limit_price = current_price * 0.945
        
        Display.info(f"Creating stop-limit order:")
        Display.info(f"  Stop trigger: ${stop_price:,.2f}")
        Display.info(f"  Limit price: ${limit_price:,.2f}")
        
        order = bot.place_stop_limit_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity=0.001,
            price=limit_price,
            stop_price=stop_price
        )
        
        Display.order_result(order, "Stop-Limit Order")
        
        # Clean up: cancel the order
        Display.info("Cleaning up - cancelling order...")
        bot.cancel_order("BTCUSDT", order['orderId'])
        Display.success("Order cancelled")
        
    except Exception as e:
        Display.error(f"Stop-limit error: {e}")


def demonstrate_take_profit(bot: BasicBot):
    """Demonstrate take-profit order placement."""
    Display.info("=== Take-Profit Order Example ===")
    
    try:
        current_price = bot.get_symbol_price("BTCUSDT")
        Display.price("BTCUSDT", current_price)
        
        # Take-profit sell order: triggers and executes at 110%
        tp_price = current_price * 1.10
        
        Display.info(f"Creating take-profit order:")
        Display.info(f"  Take-profit price: ${tp_price:,.2f}")
        
        order = bot.place_take_profit_order(
            symbol="BTCUSDT",
            side="SELL",
            quantity=0.001,
            price=tp_price,
            stop_price=tp_price
        )
        
        Display.order_result(order, "Take-Profit Order")
        
        # Clean up
        Display.info("Cleaning up - cancelling order...")
        bot.cancel_order("BTCUSDT", order['orderId'])
        Display.success("Order cancelled")
        
    except Exception as e:
        Display.error(f"Take-profit error: {e}")


def demonstrate_oco(bot: BasicBot):
    """Demonstrate OCO order placement."""
    Display.info("=== OCO Order Example ===")
    Display.warning("Note: OCO requires an open position. Creating test position first...")
    
    try:
        current_price = bot.get_symbol_price("BTCUSDT")
        Display.price("BTCUSDT", current_price)
        
        # First, create a small position
        Display.info("Opening a small long position...")
        entry_order = bot.place_market_order("BTCUSDT", "BUY", 0.001)
        Display.order_result(entry_order, "Entry Order")
        
        # Now place OCO to manage the position
        tp_price = current_price * 1.05  # 5% profit
        sl_trigger = current_price * 0.97  # 3% loss trigger
        sl_limit = current_price * 0.965  # 3.5% loss limit
        
        Display.info(f"Creating OCO exit orders:")
        Display.info(f"  Take-profit: ${tp_price:,.2f}")
        Display.info(f"  Stop-loss trigger: ${sl_trigger:,.2f}")
        Display.info(f"  Stop-loss limit: ${sl_limit:,.2f}")
        
        oco_orders = bot.place_oco_order(
            symbol="BTCUSDT",
            side="SELL",  # Exit long position
            quantity=0.001,
            price=tp_price,
            stop_price=sl_trigger,
            stop_limit_price=sl_limit
        )
        
        for i, order in enumerate(oco_orders, 1):
            Display.order_result(order, f"OCO Leg {i}")
        
        # Clean up: close position and cancel orders
        Display.info("Cleaning up...")
        bot.cancel_all_orders("BTCUSDT")
        bot.place_market_order("BTCUSDT", "SELL", 0.001)
        Display.success("Position closed and orders cancelled")
        
    except Exception as e:
        Display.error(f"OCO error: {e}")
        # Try to clean up
        try:
            bot.cancel_all_orders("BTCUSDT")
        except:
            pass


def main():
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        Display.error("Please set BINANCE_API_KEY and BINANCE_API_SECRET")
        return
    
    Display.header()
    
    try:
        bot = BasicBot(api_key, api_secret, testnet=True)
        Display.success("Bot initialized!")
    except Exception as e:
        Display.error(f"Init failed: {e}")
        return
    
    # Run demonstrations
    Display.separator()
    demonstrate_stop_limit(bot)
    
    Display.separator()
    demonstrate_take_profit(bot)
    
    Display.separator()
    demonstrate_oco(bot)
    
    Display.separator()
    Display.success("Advanced orders demonstration complete!")


if __name__ == '__main__':
    main()

