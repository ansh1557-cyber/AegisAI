"""
Test Symbol Information
"""

import MetaTrader5 as mt5
from engine.mt5_connector import MT5Connector
from engine.symbol_info import SymbolInfo

MT5Connector().connect()

info = SymbolInfo().get()

print("\n========== SYMBOL INFO ==========\n")

for key, value in info.items():
    print(f"{key}: {value}")

mt5.shutdown()