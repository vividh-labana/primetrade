"""
Unit tests for the validators module.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validators import (
    validate_symbol,
    validate_side,
    validate_quantity,
    validate_price,
    validate_leverage,
    validate_time_in_force,
    ValidationError
)


class TestValidateSymbol:
    """Tests for validate_symbol function."""
    
    def test_valid_usdt_symbol(self):
        assert validate_symbol("BTCUSDT") == "BTCUSDT"
        assert validate_symbol("btcusdt") == "BTCUSDT"
        assert validate_symbol("  ETHUSDT  ") == "ETHUSDT"
    
    def test_valid_busd_symbol(self):
        assert validate_symbol("BTCBUSD") == "BTCBUSD"
    
    def test_invalid_empty_symbol(self):
        with pytest.raises(ValidationError):
            validate_symbol("")
    
    def test_invalid_short_symbol(self):
        with pytest.raises(ValidationError):
            validate_symbol("BTC")
    
    def test_invalid_suffix(self):
        with pytest.raises(ValidationError):
            validate_symbol("BTCEUR")


class TestValidateSide:
    """Tests for validate_side function."""
    
    def test_valid_buy(self):
        assert validate_side("BUY") == "BUY"
        assert validate_side("buy") == "BUY"
        assert validate_side("  Buy  ") == "BUY"
    
    def test_valid_sell(self):
        assert validate_side("SELL") == "SELL"
        assert validate_side("sell") == "SELL"
    
    def test_invalid_side(self):
        with pytest.raises(ValidationError):
            validate_side("HOLD")
    
    def test_empty_side(self):
        with pytest.raises(ValidationError):
            validate_side("")


class TestValidateQuantity:
    """Tests for validate_quantity function."""
    
    def test_valid_quantity(self):
        assert validate_quantity(1.0) == 1.0
        assert validate_quantity(0.001) == 0.001
        assert validate_quantity("0.5") == 0.5
    
    def test_zero_quantity(self):
        with pytest.raises(ValidationError):
            validate_quantity(0)
    
    def test_negative_quantity(self):
        with pytest.raises(ValidationError):
            validate_quantity(-1.0)
    
    def test_below_minimum(self):
        with pytest.raises(ValidationError):
            validate_quantity(0.0001, min_qty=0.001)
    
    def test_invalid_string(self):
        with pytest.raises(ValidationError):
            validate_quantity("abc")


class TestValidatePrice:
    """Tests for validate_price function."""
    
    def test_valid_price(self):
        assert validate_price(50000.0) == 50000.0
        assert validate_price("100.5") == 100.5
    
    def test_zero_price(self):
        with pytest.raises(ValidationError):
            validate_price(0)
    
    def test_negative_price(self):
        with pytest.raises(ValidationError):
            validate_price(-100)


class TestValidateLeverage:
    """Tests for validate_leverage function."""
    
    def test_valid_leverage(self):
        assert validate_leverage(1) == 1
        assert validate_leverage(10) == 10
        assert validate_leverage(125) == 125
    
    def test_leverage_too_low(self):
        with pytest.raises(ValidationError):
            validate_leverage(0)
    
    def test_leverage_too_high(self):
        with pytest.raises(ValidationError):
            validate_leverage(126)


class TestValidateTimeInForce:
    """Tests for validate_time_in_force function."""
    
    def test_valid_tif(self):
        assert validate_time_in_force("GTC") == "GTC"
        assert validate_time_in_force("ioc") == "IOC"
        assert validate_time_in_force("FOK") == "FOK"
    
    def test_invalid_tif(self):
        with pytest.raises(ValidationError):
            validate_time_in_force("INVALID")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

