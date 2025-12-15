"""
Binance Futures Trading Bot
A simplified trading bot for Binance Futures Testnet (USDT-M).
Supports market, limit, stop-limit, and OCO orders.
"""

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException
from typing import Optional, Dict, Any, List
from decimal import Decimal, ROUND_DOWN
import time

from logger import setup_logger, get_logger
from config import BotConfig


class BasicBot:
    """
    A trading bot for Binance Futures Testnet.
    
    Supports:
    - Market orders (buy/sell)
    - Limit orders (buy/sell)
    - Stop-Limit orders
    - OCO (One-Cancels-Other) orders
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize the trading bot.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Whether to use testnet (default: True)
        """
        self.logger = setup_logger()
        self.testnet = testnet
        
        # Initialize client
        self.client = Client(api_key, api_secret, testnet=testnet)
        
        if testnet:
            # Set testnet URLs for Futures
            self.client.FUTURES_URL = "https://testnet.binancefuture.com/fapi"
            self.logger.info("Initialized bot with Binance Futures TESTNET")
        else:
            self.logger.warning("WARNING: Using LIVE Binance Futures!")
        
        # Cache for symbol info
        self._symbol_info_cache: Dict[str, Dict] = {}
        
        self.logger.info("Trading bot initialized successfully")
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get futures account information.
        
        Returns:
            Account information dictionary
        """
        try:
            self.logger.debug("Fetching account information...")
            account = self.client.futures_account()
            
            self.logger.info(f"Account Balance: {account['totalWalletBalance']} USDT")
            self.logger.info(f"Available Balance: {account['availableBalance']} USDT")
            
            return account
        except BinanceAPIException as e:
            self.logger.error(f"API Error getting account info: {e.message}")
            raise
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get trading rules and filters for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Symbol information dictionary
        """
        if symbol in self._symbol_info_cache:
            return self._symbol_info_cache[symbol]
        
        try:
            self.logger.debug(f"Fetching symbol info for {symbol}...")
            exchange_info = self.client.futures_exchange_info()
            
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    self._symbol_info_cache[symbol] = s
                    return s
            
            raise ValueError(f"Symbol {symbol} not found")
        except BinanceAPIException as e:
            self.logger.error(f"API Error getting symbol info: {e.message}")
            raise
    
    def get_symbol_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current price
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            self.logger.debug(f"Current {symbol} price: {price}")
            return price
        except BinanceAPIException as e:
            self.logger.error(f"API Error getting price: {e.message}")
            raise
    
    def _get_precision(self, symbol: str) -> tuple:
        """
        Get price and quantity precision for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Tuple of (price_precision, quantity_precision)
        """
        info = self.get_symbol_info(symbol)
        price_precision = info['pricePrecision']
        qty_precision = info['quantityPrecision']
        return price_precision, qty_precision
    
    def _format_quantity(self, symbol: str, quantity: float) -> str:
        """Format quantity according to symbol precision."""
        _, qty_precision = self._get_precision(symbol)
        qty = Decimal(str(quantity)).quantize(
            Decimal(10) ** -qty_precision,
            rounding=ROUND_DOWN
        )
        return str(qty)
    
    def _format_price(self, symbol: str, price: float) -> str:
        """Format price according to symbol precision."""
        price_precision, _ = self._get_precision(symbol)
        formatted = Decimal(str(price)).quantize(
            Decimal(10) ** -price_precision,
            rounding=ROUND_DOWN
        )
        return str(formatted)
    
    def _validate_order_params(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: Optional[float] = None
    ) -> None:
        """
        Validate order parameters.
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Order price (optional for market orders)
            
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate side
        if side.upper() not in ['BUY', 'SELL']:
            raise ValueError(f"Invalid order side: {side}. Must be 'BUY' or 'SELL'")
        
        # Validate quantity
        if quantity <= 0:
            raise ValueError(f"Invalid quantity: {quantity}. Must be positive")
        
        # Validate price if provided
        if price is not None and price <= 0:
            raise ValueError(f"Invalid price: {price}. Must be positive")
        
        # Validate symbol exists
        self.get_symbol_info(symbol)
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Dict[str, Any]:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            
        Returns:
            Order response dictionary
        """
        self._validate_order_params(symbol, side, quantity)
        
        formatted_qty = self._format_quantity(symbol, quantity)
        
        self.logger.info(f"Placing MARKET {side} order: {formatted_qty} {symbol}")
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type=ORDER_TYPE_MARKET,
                quantity=formatted_qty
            )
            
            self.logger.info(f"✓ Order placed successfully!")
            self._log_order_details(order)
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error: {e.message}")
            raise
        except BinanceOrderException as e:
            self.logger.error(f"Order Error: {e.message}")
            raise
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK)
            
        Returns:
            Order response dictionary
        """
        self._validate_order_params(symbol, side, quantity, price)
        
        formatted_qty = self._format_quantity(symbol, quantity)
        formatted_price = self._format_price(symbol, price)
        
        self.logger.info(
            f"Placing LIMIT {side} order: {formatted_qty} {symbol} @ {formatted_price}"
        )
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type=ORDER_TYPE_LIMIT,
                quantity=formatted_qty,
                price=formatted_price,
                timeInForce=time_in_force
            )
            
            self.logger.info(f"✓ Order placed successfully!")
            self._log_order_details(order)
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error: {e.message}")
            raise
        except BinanceOrderException as e:
            self.logger.error(f"Order Error: {e.message}")
            raise
    
    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order.
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Limit price (execution price)
            stop_price: Stop price (trigger price)
            time_in_force: Time in force
            
        Returns:
            Order response dictionary
        """
        self._validate_order_params(symbol, side, quantity, price)
        
        if stop_price <= 0:
            raise ValueError(f"Invalid stop price: {stop_price}")
        
        formatted_qty = self._format_quantity(symbol, quantity)
        formatted_price = self._format_price(symbol, price)
        formatted_stop = self._format_price(symbol, stop_price)
        
        self.logger.info(
            f"Placing STOP-LIMIT {side} order: {formatted_qty} {symbol} "
            f"@ {formatted_price} (stop: {formatted_stop})"
        )
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type=FUTURE_ORDER_TYPE_STOP,
                quantity=formatted_qty,
                price=formatted_price,
                stopPrice=formatted_stop,
                timeInForce=time_in_force
            )
            
            self.logger.info(f"✓ Stop-Limit order placed successfully!")
            self._log_order_details(order)
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error: {e.message}")
            raise
        except BinanceOrderException as e:
            self.logger.error(f"Order Error: {e.message}")
            raise
    
    def place_take_profit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place a take-profit order.
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Limit price
            stop_price: Take profit trigger price
            time_in_force: Time in force
            
        Returns:
            Order response dictionary
        """
        self._validate_order_params(symbol, side, quantity, price)
        
        formatted_qty = self._format_quantity(symbol, quantity)
        formatted_price = self._format_price(symbol, price)
        formatted_stop = self._format_price(symbol, stop_price)
        
        self.logger.info(
            f"Placing TAKE-PROFIT {side} order: {formatted_qty} {symbol} "
            f"@ {formatted_price} (trigger: {formatted_stop})"
        )
        
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type=FUTURE_ORDER_TYPE_TAKE_PROFIT,
                quantity=formatted_qty,
                price=formatted_price,
                stopPrice=formatted_stop,
                timeInForce=time_in_force
            )
            
            self.logger.info(f"✓ Take-Profit order placed successfully!")
            self._log_order_details(order)
            
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error: {e.message}")
            raise
        except BinanceOrderException as e:
            self.logger.error(f"Order Error: {e.message}")
            raise
    
    def place_oco_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        stop_limit_price: float,
        time_in_force: str = "GTC"
    ) -> List[Dict[str, Any]]:
        """
        Place an OCO (One-Cancels-Other) order.
        This creates both a take-profit and stop-loss order.
        
        Note: Binance Futures doesn't have native OCO, so we simulate it
        by placing both a take-profit and stop-loss order.
        
        Args:
            symbol: Trading pair symbol
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Take-profit price
            stop_price: Stop-loss trigger price
            stop_limit_price: Stop-loss limit price
            time_in_force: Time in force
            
        Returns:
            List of order response dictionaries
        """
        self._validate_order_params(symbol, side, quantity, price)
        
        formatted_qty = self._format_quantity(symbol, quantity)
        formatted_tp_price = self._format_price(symbol, price)
        formatted_stop = self._format_price(symbol, stop_price)
        formatted_stop_limit = self._format_price(symbol, stop_limit_price)
        
        self.logger.info(
            f"Placing OCO {side} order: {formatted_qty} {symbol} "
            f"TP: {formatted_tp_price} / SL: {formatted_stop}"
        )
        
        orders = []
        
        try:
            # Place take-profit order
            tp_order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type=FUTURE_ORDER_TYPE_TAKE_PROFIT,
                quantity=formatted_qty,
                price=formatted_tp_price,
                stopPrice=formatted_tp_price,
                timeInForce=time_in_force,
                reduceOnly=True
            )
            orders.append(tp_order)
            self.logger.info("✓ Take-Profit leg placed")
            
            # Place stop-loss order
            sl_order = self.client.futures_create_order(
                symbol=symbol,
                side=side.upper(),
                type=FUTURE_ORDER_TYPE_STOP,
                quantity=formatted_qty,
                price=formatted_stop_limit,
                stopPrice=formatted_stop,
                timeInForce=time_in_force,
                reduceOnly=True
            )
            orders.append(sl_order)
            self.logger.info("✓ Stop-Loss leg placed")
            
            self.logger.info(f"✓ OCO order placed successfully!")
            for order in orders:
                self._log_order_details(order)
            
            return orders
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error placing OCO: {e.message}")
            # Cancel any orders that were placed if one fails
            for order in orders:
                try:
                    self.cancel_order(symbol, order['orderId'])
                except Exception:
                    pass
            raise
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open orders.
        
        Args:
            symbol: Optional symbol to filter orders
            
        Returns:
            List of open orders
        """
        try:
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                orders = self.client.futures_get_open_orders()
            
            self.logger.info(f"Found {len(orders)} open order(s)")
            return orders
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error getting open orders: {e.message}")
            raise
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get the status of a specific order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        try:
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            self._log_order_details(order)
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error getting order status: {e.message}")
            raise
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an open order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel
            
        Returns:
            Cancelled order details
        """
        self.logger.info(f"Cancelling order {order_id} for {symbol}...")
        
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            self.logger.info(f"✓ Order {order_id} cancelled successfully")
            return result
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error cancelling order: {e.message}")
            raise
    
    def cancel_all_orders(self, symbol: str) -> Dict[str, Any]:
        """
        Cancel all open orders for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Cancellation result
        """
        self.logger.info(f"Cancelling all orders for {symbol}...")
        
        try:
            result = self.client.futures_cancel_all_open_orders(symbol=symbol)
            self.logger.info(f"✓ All orders for {symbol} cancelled")
            return result
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error cancelling all orders: {e.message}")
            raise
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get current positions.
        
        Args:
            symbol: Optional symbol to filter
            
        Returns:
            List of positions
        """
        try:
            positions = self.client.futures_position_information()
            
            if symbol:
                positions = [p for p in positions if p['symbol'] == symbol]
            
            # Filter out empty positions
            active_positions = [
                p for p in positions 
                if float(p['positionAmt']) != 0
            ]
            
            self.logger.info(f"Found {len(active_positions)} active position(s)")
            return active_positions
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error getting positions: {e.message}")
            raise
    
    def set_leverage(self, symbol: str, leverage: int) -> Dict[str, Any]:
        """
        Set leverage for a symbol.
        
        Args:
            symbol: Trading pair symbol
            leverage: Leverage value (1-125)
            
        Returns:
            Leverage change result
        """
        if not 1 <= leverage <= 125:
            raise ValueError(f"Leverage must be between 1 and 125, got {leverage}")
        
        self.logger.info(f"Setting leverage for {symbol} to {leverage}x")
        
        try:
            result = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            self.logger.info(f"✓ Leverage set to {leverage}x for {symbol}")
            return result
            
        except BinanceAPIException as e:
            self.logger.error(f"API Error setting leverage: {e.message}")
            raise
    
    def _log_order_details(self, order: Dict[str, Any]) -> None:
        """Log order details in a formatted way."""
        self.logger.info("-" * 50)
        self.logger.info(f"Order ID: {order.get('orderId', 'N/A')}")
        self.logger.info(f"Symbol: {order.get('symbol', 'N/A')}")
        self.logger.info(f"Side: {order.get('side', 'N/A')}")
        self.logger.info(f"Type: {order.get('type', 'N/A')}")
        self.logger.info(f"Quantity: {order.get('origQty', 'N/A')}")
        
        if order.get('price') and float(order.get('price', 0)) > 0:
            self.logger.info(f"Price: {order.get('price')}")
        
        if order.get('stopPrice') and float(order.get('stopPrice', 0)) > 0:
            self.logger.info(f"Stop Price: {order.get('stopPrice')}")
        
        self.logger.info(f"Status: {order.get('status', 'N/A')}")
        
        if order.get('avgPrice') and float(order.get('avgPrice', 0)) > 0:
            self.logger.info(f"Avg Fill Price: {order.get('avgPrice')}")
        
        self.logger.info("-" * 50)


def create_bot_from_config(config: BotConfig) -> BasicBot:
    """Create a BasicBot instance from configuration."""
    return BasicBot(
        api_key=config.api_key,
        api_secret=config.api_secret,
        testnet=config.testnet
    )

