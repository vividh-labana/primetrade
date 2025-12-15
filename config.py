"""
Configuration module for the Binance Trading Bot.
Handles API credentials and testnet configuration.
"""

import os
from dataclasses import dataclass


@dataclass
class BotConfig:
    """Configuration settings for the trading bot."""
    api_key: str
    api_secret: str
    testnet: bool = True
    
    # Binance Futures Testnet base URL
    TESTNET_BASE_URL = "https://testnet.binancefuture.com"
    
    # Default trading parameters
    DEFAULT_SYMBOL = "BTCUSDT"
    DEFAULT_LEVERAGE = 1


def load_config_from_env() -> BotConfig:
    """Load configuration from environment variables."""
    api_key = os.getenv("BINANCE_API_KEY", "")
    api_secret = os.getenv("BINANCE_API_SECRET", "")
    
    if not api_key or not api_secret:
        raise ValueError(
            "Missing API credentials. Please set BINANCE_API_KEY and BINANCE_API_SECRET "
            "environment variables or create a .env file."
        )
    
    return BotConfig(api_key=api_key, api_secret=api_secret, testnet=True)

