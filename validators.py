"""
Input validation utilities for the trading bot.
Provides comprehensive validation for all order parameters.
"""

from typing import Optional, Tuple
from decimal import Decimal, InvalidOperation


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate trading pair symbol format.
    
    Args:
        symbol: Trading pair symbol
        
    Returns:
        Normalized symbol (uppercase)
        
    Raises:
        ValidationError: If symbol is invalid
    """
    if not symbol:
        raise ValidationError("Symbol cannot be empty")
    
    symbol = symbol.strip().upper()
    
    if len(symbol) < 5:
        raise ValidationError(f"Invalid symbol format: {symbol}")
    
    # Check for common USDT pairs
    if not symbol.endswith(('USDT', 'BUSD', 'BTC', 'ETH')):
        raise ValidationError(
            f"Invalid symbol: {symbol}. Must end with USDT, BUSD, BTC, or ETH"
        )
    
    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.
    
    Args:
        side: Order side (BUY or SELL)
        
    Returns:
        Normalized side (uppercase)
        
    Raises:
        ValidationError: If side is invalid
    """
    if not side:
        raise ValidationError("Side cannot be empty")
    
    side = side.strip().upper()
    
    if side not in ['BUY', 'SELL']:
        raise ValidationError(f"Invalid side: {side}. Must be 'BUY' or 'SELL'")
    
    return side


def validate_quantity(quantity: float, min_qty: float = 0.0) -> float:
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity
        min_qty: Minimum allowed quantity
        
    Returns:
        Validated quantity
        
    Raises:
        ValidationError: If quantity is invalid
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid quantity: {quantity}")
    
    if qty <= 0:
        raise ValidationError(f"Quantity must be positive, got: {qty}")
    
    if qty < min_qty:
        raise ValidationError(f"Quantity {qty} is below minimum {min_qty}")
    
    return qty


def validate_price(price: float, name: str = "Price") -> float:
    """
    Validate order price.
    
    Args:
        price: Order price
        name: Name for error messages
        
    Returns:
        Validated price
        
    Raises:
        ValidationError: If price is invalid
    """
    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid {name}: {price}")
    
    if p <= 0:
        raise ValidationError(f"{name} must be positive, got: {p}")
    
    return p


def validate_leverage(leverage: int) -> int:
    """
    Validate leverage value.
    
    Args:
        leverage: Leverage multiplier
        
    Returns:
        Validated leverage
        
    Raises:
        ValidationError: If leverage is invalid
    """
    try:
        lev = int(leverage)
    except (ValueError, TypeError):
        raise ValidationError(f"Invalid leverage: {leverage}")
    
    if lev < 1 or lev > 125:
        raise ValidationError(f"Leverage must be between 1 and 125, got: {lev}")
    
    return lev


def validate_time_in_force(tif: str) -> str:
    """
    Validate time in force parameter.
    
    Args:
        tif: Time in force value
        
    Returns:
        Validated TIF value
        
    Raises:
        ValidationError: If TIF is invalid
    """
    valid_tifs = ['GTC', 'IOC', 'FOK', 'GTX']
    
    tif = tif.strip().upper()
    
    if tif not in valid_tifs:
        raise ValidationError(
            f"Invalid time in force: {tif}. Valid options: {', '.join(valid_tifs)}"
        )
    
    return tif


def validate_order_params(
    symbol: str,
    side: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None
) -> Tuple[str, str, float, Optional[float], Optional[float]]:
    """
    Validate all order parameters at once.
    
    Args:
        symbol: Trading pair symbol
        side: Order side
        quantity: Order quantity
        price: Order price (optional)
        stop_price: Stop price (optional)
        
    Returns:
        Tuple of validated parameters
        
    Raises:
        ValidationError: If any parameter is invalid
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_qty = validate_quantity(quantity)
    
    validated_price = None
    if price is not None:
        validated_price = validate_price(price, "Price")
    
    validated_stop = None
    if stop_price is not None:
        validated_stop = validate_price(stop_price, "Stop price")
    
    return (
        validated_symbol,
        validated_side,
        validated_qty,
        validated_price,
        validated_stop
    )


def format_decimal(value: float, precision: int) -> str:
    """
    Format a float to a specific decimal precision.
    
    Args:
        value: Value to format
        precision: Number of decimal places
        
    Returns:
        Formatted string
    """
    try:
        d = Decimal(str(value))
        format_str = f'0.{"0" * precision}'
        return str(d.quantize(Decimal(format_str)))
    except InvalidOperation:
        return str(value)

