"""
Aegis AI
Test: Fair Value Gap Engine
Version: 0.3.1
"""

from engine.mt5_connector import MT5Connector
from engine.fvg import FVGEngine

connector = MT5Connector()
connector.connect()

df = connector.get_rates(symbol="XAUUSD", bars=200)

fvg = FVGEngine()
result = fvg.detect(df)

print("Bullish FVGs:", len(result["bullish_fvg"]))
print("Bearish FVGs:", len(result["bearish_fvg"]))

print()
print("Last 3 Bullish FVGs")
print(result["bullish_fvg"][-3:])

print()
print("Last 3 Bearish FVGs")
print(result["bearish_fvg"][-3:])

connector.disconnect()