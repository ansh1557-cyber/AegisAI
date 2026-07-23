"""
Aegis AI
Test: Order Block Engine
Version: 0.4.0
"""

from engine.mt5_connector import MT5Connector
from engine.order_block import OrderBlockEngine


connector = MT5Connector()
connector.connect()

df = connector.get_rates(
    symbol="XAUUSD",
    bars=500
)

engine = OrderBlockEngine()

result = engine.detect(df)

print("Bullish Order Blocks:", len(result["bullish_blocks"]))
print("Bearish Order Blocks:", len(result["bearish_blocks"]))

print("\nLast 3 Bullish Order Blocks")
print(result["bullish_blocks"][-3:])

print("\nLast 3 Bearish Order Blocks")
print(result["bearish_blocks"][-3:])

connector.disconnect()