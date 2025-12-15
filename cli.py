#!/usr/bin/env python3
"""
Command-line interface for the Binance Futures Trading Bot.
Provides interactive and command-based order placement.
"""

import argparse
import os
import sys
from typing import Optional
from dotenv import load_dotenv
from tabulate import tabulate
from colorama import init, Fore, Style

from bot import BasicBot
from config import load_config_from_env, BotConfig
from logger import setup_logger, get_logger


# Initialize colorama for cross-platform color support
init()


def print_header():
    """Print the application header."""
    header = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║     🚀 Binance Futures Trading Bot - TESTNET 🚀               ║
║                                                                ║
║     ⚠️  This bot is for TESTNET use only!                     ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(header)


def print_success(message: str):
    """Print success message."""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message."""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message."""
    print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def validate_positive_float(value: str, name: str) -> float:
    """Validate and convert string to positive float."""
    try:
        result = float(value)
        if result <= 0:
            raise ValueError(f"{name} must be positive")
        return result
    except ValueError:
        raise ValueError(f"Invalid {name}: {value}")


def validate_side(side: str) -> str:
    """Validate order side."""
    side = side.upper()
    if side not in ['BUY', 'SELL']:
        raise ValueError(f"Invalid side: {side}. Must be 'BUY' or 'SELL'")
    return side


def display_order_result(order: dict):
    """Display order result in a formatted table."""
    data = [
        ["Order ID", order.get('orderId', 'N/A')],
        ["Symbol", order.get('symbol', 'N/A')],
        ["Side", order.get('side', 'N/A')],
        ["Type", order.get('type', 'N/A')],
        ["Quantity", order.get('origQty', 'N/A')],
        ["Price", order.get('price', 'Market')],
        ["Stop Price", order.get('stopPrice', 'N/A')],
        ["Status", order.get('status', 'N/A')],
        ["Time in Force", order.get('timeInForce', 'N/A')],
    ]
    
    print(f"\n{Fore.GREEN}Order Details:{Style.RESET_ALL}")
    print(tabulate(data, tablefmt="rounded_outline"))


def display_positions(positions: list):
    """Display positions in a formatted table."""
    if not positions:
        print_info("No active positions")
        return
    
    headers = ["Symbol", "Side", "Size", "Entry Price", "Mark Price", "PnL", "Leverage"]
    data = []
    
    for pos in positions:
        amt = float(pos.get('positionAmt', 0))
        side = "LONG" if amt > 0 else "SHORT"
        pnl = float(pos.get('unrealizedProfit', 0))
        pnl_color = Fore.GREEN if pnl >= 0 else Fore.RED
        
        data.append([
            pos.get('symbol', 'N/A'),
            side,
            abs(amt),
            pos.get('entryPrice', 'N/A'),
            pos.get('markPrice', 'N/A'),
            f"{pnl_color}{pnl:.4f}{Style.RESET_ALL}",
            pos.get('leverage', 'N/A')
        ])
    
    print(f"\n{Fore.CYAN}Active Positions:{Style.RESET_ALL}")
    print(tabulate(data, headers=headers, tablefmt="rounded_outline"))


def display_open_orders(orders: list):
    """Display open orders in a formatted table."""
    if not orders:
        print_info("No open orders")
        return
    
    headers = ["ID", "Symbol", "Side", "Type", "Qty", "Price", "Stop", "Status"]
    data = []
    
    for order in orders:
        data.append([
            order.get('orderId', 'N/A'),
            order.get('symbol', 'N/A'),
            order.get('side', 'N/A'),
            order.get('type', 'N/A'),
            order.get('origQty', 'N/A'),
            order.get('price', 'N/A'),
            order.get('stopPrice', 'N/A'),
            order.get('status', 'N/A')
        ])
    
    print(f"\n{Fore.CYAN}Open Orders:{Style.RESET_ALL}")
    print(tabulate(data, headers=headers, tablefmt="rounded_outline"))


def interactive_mode(bot: BasicBot):
    """Run the bot in interactive mode."""
    print_header()
    print_info("Interactive mode activated. Type 'help' for commands.\n")
    
    commands = {
        'help': 'Show available commands',
        'market': 'Place a market order',
        'limit': 'Place a limit order',
        'stop': 'Place a stop-limit order',
        'oco': 'Place an OCO order (take-profit + stop-loss)',
        'positions': 'Show current positions',
        'orders': 'Show open orders',
        'cancel': 'Cancel an order',
        'cancelall': 'Cancel all orders for a symbol',
        'account': 'Show account info',
        'price': 'Get current price for a symbol',
        'leverage': 'Set leverage for a symbol',
        'quit': 'Exit the bot'
    }
    
    while True:
        try:
            user_input = input(f"\n{Fore.CYAN}bot > {Style.RESET_ALL}").strip().lower()
            
            if not user_input:
                continue
            
            if user_input == 'help':
                print(f"\n{Fore.CYAN}Available Commands:{Style.RESET_ALL}")
                for cmd, desc in commands.items():
                    print(f"  {Fore.GREEN}{cmd:12}{Style.RESET_ALL} - {desc}")
            
            elif user_input == 'market':
                symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
                side = validate_side(input("Side (BUY/SELL): ").strip())
                quantity = validate_positive_float(input("Quantity: ").strip(), "quantity")
                
                print_info(f"Placing MARKET {side} order for {quantity} {symbol}...")
                order = bot.place_market_order(symbol, side, quantity)
                display_order_result(order)
                print_success("Market order placed!")
            
            elif user_input == 'limit':
                symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
                side = validate_side(input("Side (BUY/SELL): ").strip())
                quantity = validate_positive_float(input("Quantity: ").strip(), "quantity")
                price = validate_positive_float(input("Price: ").strip(), "price")
                
                print_info(f"Placing LIMIT {side} order for {quantity} {symbol} @ {price}...")
                order = bot.place_limit_order(symbol, side, quantity, price)
                display_order_result(order)
                print_success("Limit order placed!")
            
            elif user_input == 'stop':
                symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
                side = validate_side(input("Side (BUY/SELL): ").strip())
                quantity = validate_positive_float(input("Quantity: ").strip(), "quantity")
                stop_price = validate_positive_float(input("Stop Price (trigger): ").strip(), "stop price")
                price = validate_positive_float(input("Limit Price (execution): ").strip(), "limit price")
                
                print_info(f"Placing STOP-LIMIT {side} order...")
                order = bot.place_stop_limit_order(symbol, side, quantity, price, stop_price)
                display_order_result(order)
                print_success("Stop-Limit order placed!")
            
            elif user_input == 'oco':
                symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
                side = validate_side(input("Side (BUY/SELL): ").strip())
                quantity = validate_positive_float(input("Quantity: ").strip(), "quantity")
                tp_price = validate_positive_float(input("Take-Profit Price: ").strip(), "take-profit price")
                sl_trigger = validate_positive_float(input("Stop-Loss Trigger Price: ").strip(), "stop-loss trigger")
                sl_limit = validate_positive_float(input("Stop-Loss Limit Price: ").strip(), "stop-loss limit")
                
                print_info(f"Placing OCO order (TP: {tp_price}, SL: {sl_trigger})...")
                orders = bot.place_oco_order(symbol, side, quantity, tp_price, sl_trigger, sl_limit)
                for order in orders:
                    display_order_result(order)
                print_success("OCO order placed!")
            
            elif user_input == 'positions':
                symbol = input("Symbol (leave empty for all): ").strip().upper() or None
                positions = bot.get_positions(symbol)
                display_positions(positions)
            
            elif user_input == 'orders':
                symbol = input("Symbol (leave empty for all): ").strip().upper() or None
                orders = bot.get_open_orders(symbol)
                display_open_orders(orders)
            
            elif user_input == 'cancel':
                symbol = input("Symbol: ").strip().upper()
                order_id = int(input("Order ID: ").strip())
                bot.cancel_order(symbol, order_id)
                print_success(f"Order {order_id} cancelled!")
            
            elif user_input == 'cancelall':
                symbol = input("Symbol: ").strip().upper()
                confirm = input(f"Cancel ALL orders for {symbol}? (yes/no): ").strip().lower()
                if confirm == 'yes':
                    bot.cancel_all_orders(symbol)
                    print_success(f"All orders for {symbol} cancelled!")
                else:
                    print_info("Cancelled")
            
            elif user_input == 'account':
                account = bot.get_account_info()
                data = [
                    ["Total Balance", f"{float(account['totalWalletBalance']):.4f} USDT"],
                    ["Available Balance", f"{float(account['availableBalance']):.4f} USDT"],
                    ["Unrealized PnL", f"{float(account['totalUnrealizedProfit']):.4f} USDT"],
                    ["Margin Balance", f"{float(account['totalMarginBalance']):.4f} USDT"],
                ]
                print(f"\n{Fore.CYAN}Account Info:{Style.RESET_ALL}")
                print(tabulate(data, tablefmt="rounded_outline"))
            
            elif user_input == 'price':
                symbol = input("Symbol (e.g., BTCUSDT): ").strip().upper()
                price = bot.get_symbol_price(symbol)
                print_info(f"{symbol} current price: {Fore.GREEN}${price:,.2f}{Style.RESET_ALL}")
            
            elif user_input == 'leverage':
                symbol = input("Symbol: ").strip().upper()
                leverage = int(input("Leverage (1-125): ").strip())
                bot.set_leverage(symbol, leverage)
                print_success(f"Leverage set to {leverage}x for {symbol}")
            
            elif user_input in ['quit', 'exit', 'q']:
                print_info("Goodbye! 👋")
                break
            
            else:
                print_error(f"Unknown command: {user_input}. Type 'help' for available commands.")
        
        except KeyboardInterrupt:
            print("\n")
            print_info("Goodbye! 👋")
            break
        except ValueError as e:
            print_error(str(e))
        except Exception as e:
            print_error(f"Error: {str(e)}")


def command_mode(args: argparse.Namespace, bot: BasicBot):
    """Execute a single command based on arguments."""
    try:
        if args.command == 'market':
            order = bot.place_market_order(args.symbol, args.side, args.quantity)
            display_order_result(order)
            print_success("Market order placed!")
        
        elif args.command == 'limit':
            if args.price is None:
                print_error("Price is required for limit orders")
                return
            order = bot.place_limit_order(args.symbol, args.side, args.quantity, args.price)
            display_order_result(order)
            print_success("Limit order placed!")
        
        elif args.command == 'stop':
            if args.price is None or args.stop_price is None:
                print_error("Price and stop-price are required for stop-limit orders")
                return
            order = bot.place_stop_limit_order(
                args.symbol, args.side, args.quantity, args.price, args.stop_price
            )
            display_order_result(order)
            print_success("Stop-Limit order placed!")
        
        elif args.command == 'positions':
            positions = bot.get_positions(args.symbol if hasattr(args, 'symbol') else None)
            display_positions(positions)
        
        elif args.command == 'orders':
            orders = bot.get_open_orders(args.symbol if hasattr(args, 'symbol') else None)
            display_open_orders(orders)
        
        elif args.command == 'cancel':
            bot.cancel_order(args.symbol, args.order_id)
            print_success(f"Order {args.order_id} cancelled!")
        
        elif args.command == 'account':
            account = bot.get_account_info()
            print(f"Total Balance: {account['totalWalletBalance']} USDT")
            print(f"Available: {account['availableBalance']} USDT")
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description="Binance Futures Trading Bot - Testnet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s market -s BTCUSDT -side BUY -q 0.001
  %(prog)s limit -s BTCUSDT -side SELL -q 0.001 -p 50000
  %(prog)s stop -s BTCUSDT -side SELL -q 0.001 -p 49000 --stop-price 49500
  %(prog)s positions
  %(prog)s orders -s BTCUSDT
  %(prog)s cancel -s BTCUSDT --order-id 123456
        """
    )
    
    parser.add_argument(
        '--api-key',
        help='Binance API key (or set BINANCE_API_KEY env var)'
    )
    parser.add_argument(
        '--api-secret',
        help='Binance API secret (or set BINANCE_API_SECRET env var)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Market order
    market_parser = subparsers.add_parser('market', help='Place a market order')
    market_parser.add_argument('-s', '--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
    market_parser.add_argument('--side', '-side', required=True, choices=['BUY', 'SELL', 'buy', 'sell'])
    market_parser.add_argument('-q', '--quantity', type=float, required=True, help='Order quantity')
    
    # Limit order
    limit_parser = subparsers.add_parser('limit', help='Place a limit order')
    limit_parser.add_argument('-s', '--symbol', required=True, help='Trading pair')
    limit_parser.add_argument('--side', '-side', required=True, choices=['BUY', 'SELL', 'buy', 'sell'])
    limit_parser.add_argument('-q', '--quantity', type=float, required=True, help='Order quantity')
    limit_parser.add_argument('-p', '--price', type=float, required=True, help='Limit price')
    
    # Stop-limit order
    stop_parser = subparsers.add_parser('stop', help='Place a stop-limit order')
    stop_parser.add_argument('-s', '--symbol', required=True, help='Trading pair')
    stop_parser.add_argument('--side', '-side', required=True, choices=['BUY', 'SELL', 'buy', 'sell'])
    stop_parser.add_argument('-q', '--quantity', type=float, required=True, help='Order quantity')
    stop_parser.add_argument('-p', '--price', type=float, required=True, help='Limit price')
    stop_parser.add_argument('--stop-price', type=float, required=True, help='Stop trigger price')
    
    # Positions
    pos_parser = subparsers.add_parser('positions', help='Show current positions')
    pos_parser.add_argument('-s', '--symbol', help='Filter by symbol')
    
    # Open orders
    orders_parser = subparsers.add_parser('orders', help='Show open orders')
    orders_parser.add_argument('-s', '--symbol', help='Filter by symbol')
    
    # Cancel order
    cancel_parser = subparsers.add_parser('cancel', help='Cancel an order')
    cancel_parser.add_argument('-s', '--symbol', required=True, help='Trading pair')
    cancel_parser.add_argument('--order-id', type=int, required=True, help='Order ID to cancel')
    
    # Account info
    subparsers.add_parser('account', help='Show account information')
    
    return parser


def main():
    """Main entry point."""
    # Load environment variables
    load_dotenv()
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Get API credentials
    api_key = args.api_key or os.getenv('BINANCE_API_KEY')
    api_secret = args.api_secret or os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        print_error("Missing API credentials!")
        print_info("Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables")
        print_info("Or use --api-key and --api-secret arguments")
        print_info("\nGet your testnet credentials from: https://testnet.binancefuture.com/")
        sys.exit(1)
    
    # Setup logging
    import logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logger(level=log_level)
    
    # Initialize bot
    try:
        bot = BasicBot(api_key, api_secret, testnet=True)
    except Exception as e:
        print_error(f"Failed to initialize bot: {str(e)}")
        sys.exit(1)
    
    # Run in appropriate mode
    if args.command:
        command_mode(args, bot)
    else:
        interactive_mode(bot)


if __name__ == '__main__':
    main()

