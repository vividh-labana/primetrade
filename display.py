"""
Display utilities for the trading bot CLI.
Provides beautiful formatted output for orders, positions, and account info.
"""

from typing import Dict, List, Any, Optional
from colorama import Fore, Style, Back
from tabulate import tabulate
from datetime import datetime


class Display:
    """Enhanced display utilities for the CLI."""
    
    # Box drawing characters
    BOX_TOP_LEFT = "╔"
    BOX_TOP_RIGHT = "╗"
    BOX_BOTTOM_LEFT = "╚"
    BOX_BOTTOM_RIGHT = "╝"
    BOX_HORIZONTAL = "═"
    BOX_VERTICAL = "║"
    
    @staticmethod
    def header():
        """Display the application header."""
        width = 64
        print()
        print(f"{Fore.CYAN}{Display.BOX_TOP_LEFT}{Display.BOX_HORIZONTAL * (width - 2)}{Display.BOX_TOP_RIGHT}")
        print(f"{Display.BOX_VERTICAL}{'🚀 PRIMETRADE - Binance Futures Trading Bot 🚀'.center(width - 2)}{Display.BOX_VERTICAL}")
        print(f"{Display.BOX_VERTICAL}{''.center(width - 2)}{Display.BOX_VERTICAL}")
        print(f"{Display.BOX_VERTICAL}{'⚠️  TESTNET MODE - No Real Funds ⚠️'.center(width - 2)}{Display.BOX_VERTICAL}")
        print(f"{Display.BOX_BOTTOM_LEFT}{Display.BOX_HORIZONTAL * (width - 2)}{Display.BOX_BOTTOM_RIGHT}{Style.RESET_ALL}")
        print()
    
    @staticmethod
    def success(message: str):
        """Display success message."""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def error(message: str):
        """Display error message."""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def warning(message: str):
        """Display warning message."""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def info(message: str):
        """Display info message."""
        print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")
    
    @staticmethod
    def price(symbol: str, price: float):
        """Display price with formatting."""
        formatted = f"${price:,.2f}" if price > 100 else f"${price:,.6f}"
        print(f"\n{Fore.CYAN}📊 {symbol}{Style.RESET_ALL}: {Fore.GREEN}{formatted}{Style.RESET_ALL}")
    
    @staticmethod
    def order_result(order: Dict[str, Any], title: str = "Order Details"):
        """Display order result in a beautiful table."""
        status = order.get('status', 'UNKNOWN')
        status_color = Fore.GREEN if status in ['NEW', 'FILLED', 'PARTIALLY_FILLED'] else Fore.YELLOW
        
        side = order.get('side', 'N/A')
        side_color = Fore.GREEN if side == 'BUY' else Fore.RED
        
        data = [
            ["Order ID", f"{Fore.CYAN}{order.get('orderId', 'N/A')}{Style.RESET_ALL}"],
            ["Symbol", order.get('symbol', 'N/A')],
            ["Side", f"{side_color}{side}{Style.RESET_ALL}"],
            ["Type", order.get('type', 'N/A')],
            ["Quantity", order.get('origQty', 'N/A')],
        ]
        
        price = order.get('price')
        if price and float(price) > 0:
            data.append(["Price", f"${float(price):,.2f}"])
        
        stop_price = order.get('stopPrice')
        if stop_price and float(stop_price) > 0:
            data.append(["Stop Price", f"${float(stop_price):,.2f}"])
        
        avg_price = order.get('avgPrice')
        if avg_price and float(avg_price) > 0:
            data.append(["Avg Fill Price", f"${float(avg_price):,.2f}"])
        
        data.append(["Status", f"{status_color}{status}{Style.RESET_ALL}"])
        data.append(["Time in Force", order.get('timeInForce', 'N/A')])
        
        print(f"\n{Fore.CYAN}📋 {title}{Style.RESET_ALL}")
        print(tabulate(data, tablefmt="rounded_outline"))
    
    @staticmethod
    def positions(positions: List[Dict[str, Any]]):
        """Display positions in a formatted table."""
        if not positions:
            Display.info("No active positions")
            return
        
        headers = [
            f"{Fore.CYAN}Symbol{Style.RESET_ALL}",
            f"{Fore.CYAN}Side{Style.RESET_ALL}",
            f"{Fore.CYAN}Size{Style.RESET_ALL}",
            f"{Fore.CYAN}Entry{Style.RESET_ALL}",
            f"{Fore.CYAN}Mark{Style.RESET_ALL}",
            f"{Fore.CYAN}PnL{Style.RESET_ALL}",
            f"{Fore.CYAN}ROE%{Style.RESET_ALL}",
        ]
        
        data = []
        for pos in positions:
            amt = float(pos.get('positionAmt', 0))
            if amt == 0:
                continue
                
            side = "LONG" if amt > 0 else "SHORT"
            side_color = Fore.GREEN if amt > 0 else Fore.RED
            
            entry = float(pos.get('entryPrice', 0))
            mark = float(pos.get('markPrice', 0))
            pnl = float(pos.get('unrealizedProfit', 0))
            pnl_color = Fore.GREEN if pnl >= 0 else Fore.RED
            
            # Calculate ROE
            if entry > 0 and amt != 0:
                leverage = int(pos.get('leverage', 1))
                roe = (pnl / (abs(amt) * entry)) * 100 * leverage
            else:
                roe = 0
            
            roe_color = Fore.GREEN if roe >= 0 else Fore.RED
            
            data.append([
                pos.get('symbol', 'N/A'),
                f"{side_color}{side}{Style.RESET_ALL}",
                f"{abs(amt):.4f}",
                f"${entry:,.2f}",
                f"${mark:,.2f}",
                f"{pnl_color}{pnl:+.4f}{Style.RESET_ALL}",
                f"{roe_color}{roe:+.2f}%{Style.RESET_ALL}",
            ])
        
        print(f"\n{Fore.CYAN}📈 Active Positions{Style.RESET_ALL}")
        print(tabulate(data, headers=headers, tablefmt="rounded_outline"))
    
    @staticmethod
    def open_orders(orders: List[Dict[str, Any]]):
        """Display open orders in a formatted table."""
        if not orders:
            Display.info("No open orders")
            return
        
        headers = [
            f"{Fore.CYAN}ID{Style.RESET_ALL}",
            f"{Fore.CYAN}Symbol{Style.RESET_ALL}",
            f"{Fore.CYAN}Side{Style.RESET_ALL}",
            f"{Fore.CYAN}Type{Style.RESET_ALL}",
            f"{Fore.CYAN}Qty{Style.RESET_ALL}",
            f"{Fore.CYAN}Price{Style.RESET_ALL}",
            f"{Fore.CYAN}Stop{Style.RESET_ALL}",
        ]
        
        data = []
        for order in orders:
            side = order.get('side', 'N/A')
            side_color = Fore.GREEN if side == 'BUY' else Fore.RED
            
            price = float(order.get('price', 0))
            stop = float(order.get('stopPrice', 0))
            
            data.append([
                order.get('orderId', 'N/A'),
                order.get('symbol', 'N/A'),
                f"{side_color}{side}{Style.RESET_ALL}",
                order.get('type', 'N/A'),
                order.get('origQty', 'N/A'),
                f"${price:,.2f}" if price > 0 else "-",
                f"${stop:,.2f}" if stop > 0 else "-",
            ])
        
        print(f"\n{Fore.CYAN}📑 Open Orders{Style.RESET_ALL}")
        print(tabulate(data, headers=headers, tablefmt="rounded_outline"))
    
    @staticmethod
    def account_info(account: Dict[str, Any]):
        """Display account information."""
        total_balance = float(account.get('totalWalletBalance', 0))
        available = float(account.get('availableBalance', 0))
        unrealized_pnl = float(account.get('totalUnrealizedProfit', 0))
        margin_balance = float(account.get('totalMarginBalance', 0))
        
        pnl_color = Fore.GREEN if unrealized_pnl >= 0 else Fore.RED
        
        data = [
            ["Total Balance", f"{Fore.GREEN}${total_balance:,.4f} USDT{Style.RESET_ALL}"],
            ["Available", f"${available:,.4f} USDT"],
            ["Unrealized PnL", f"{pnl_color}${unrealized_pnl:+,.4f} USDT{Style.RESET_ALL}"],
            ["Margin Balance", f"${margin_balance:,.4f} USDT"],
        ]
        
        print(f"\n{Fore.CYAN}💰 Account Overview{Style.RESET_ALL}")
        print(tabulate(data, tablefmt="rounded_outline"))
    
    @staticmethod
    def help_menu(commands: Dict[str, str]):
        """Display help menu."""
        print(f"\n{Fore.CYAN}📚 Available Commands{Style.RESET_ALL}\n")
        
        for cmd, desc in commands.items():
            print(f"  {Fore.GREEN}{cmd:12}{Style.RESET_ALL} │ {desc}")
        
        print()
    
    @staticmethod
    def separator():
        """Print a separator line."""
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    @staticmethod
    def prompt() -> str:
        """Display the input prompt and return user input."""
        return input(f"\n{Fore.CYAN}primetrade{Style.RESET_ALL} {Fore.YELLOW}❯{Style.RESET_ALL} ").strip()
    
    @staticmethod
    def confirm(message: str) -> bool:
        """Ask for confirmation."""
        response = input(f"{Fore.YELLOW}? {message} (yes/no): {Style.RESET_ALL}").strip().lower()
        return response in ['yes', 'y']
    
    @staticmethod
    def timestamp():
        """Display current timestamp."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{Fore.MAGENTA}🕐 {now}{Style.RESET_ALL}")

