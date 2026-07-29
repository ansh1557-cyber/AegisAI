"""
Test Trade Monitor
"""

import MetaTrader5 as mt5

from engine.trade_monitor import TradeMonitor

if not mt5.initialize():
    raise Exception("Failed to connect to MT5")

monitor = TradeMonitor()

monitor.monitor()

mt5.shutdown()