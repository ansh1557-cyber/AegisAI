"""
Aegis AI
Configuration
Version: 0.4.1
"""

import MetaTrader5 as mt5

# Trading
SYMBOL = "XAUUSD"

# Timeframes
TIMEFRAME = mt5.TIMEFRAME_M15

# Data
BARS = 500

# Market Structure
SWING_LOOKBACK = 2
LIQUIDITY_LOOKAHEAD = 20

# Risk Management
ACCOUNT_BALANCE = 100
RISK_PERCENT = 1
RISK_REWARD = 2
SL_BUFFER = 2