"""
Aegis AI
Module: Timeframe Configuration
Version: 0.5.0
"""

import MetaTrader5 as mt5

TIMEFRAMES = {
    "H4": mt5.TIMEFRAME_H4,
    "H1": mt5.TIMEFRAME_H1,
    "M15": mt5.TIMEFRAME_M15,
}