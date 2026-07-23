"""
Aegis AI
Configuration
Version: 0.4.1
"""

import MetaTrader5 as mt5

# Trading Symbol
SYMBOL = "XAUUSD"

# Timeframe
TIMEFRAME = mt5.TIMEFRAME_M15

# Number of candles
BARS = 500

# Swing Detection
SWING_LOOKBACK = 2

# Liquidity
LIQUIDITY_LOOKAHEAD = 20