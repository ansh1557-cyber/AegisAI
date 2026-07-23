"""
Aegis AI
Test: Premium / Discount Engine
Version: 0.4.1
"""

from engine.mt5_connector import MT5Connector
from engine.market_structure import MarketStructureEngine
from engine.premium_discount import PremiumDiscountEngine
from engine.config import SYMBOL, TIMEFRAME, BARS


connector = MT5Connector()
connector.connect()

df = connector.get_rates(
    symbol=SYMBOL,
    timeframe=TIMEFRAME,
    bars=BARS
)

market = MarketStructureEngine()
swings = market.detect_swings(df)

engine = PremiumDiscountEngine()

result = engine.detect(
    df,
    swings["swing_highs"],
    swings["swing_lows"]
)

print("\n========== PREMIUM / DISCOUNT ==========")
print("Premium:", result["premium"])
print("Discount:", result["discount"])
print("Equilibrium:", result["equilibrium"])
print("Current Zone:", result["current_zone"])
print("========================================")

connector.disconnect()