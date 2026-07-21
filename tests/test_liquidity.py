from engine.mt5_connector import MT5Connector
from engine.market_structure import MarketStructureEngine
from engine.liquidity import LiquidityEngine

connector = MT5Connector()
connector.connect()

df = connector.get_rates(symbol="XAUUSD", bars=500)

market = MarketStructureEngine()
result = market.detect_swings(df)

liquidity = LiquidityEngine()
sweeps = liquidity.detect(
    df,
    result["swing_highs"],
    result["swing_lows"]
)

print("Buy-side Sweeps:", len(sweeps["buy_side_sweeps"]))
print("Sell-side Sweeps:", len(sweeps["sell_side_sweeps"]))

print("\nLast 3 Buy-side Sweeps")
print(sweeps["buy_side_sweeps"][-3:])

print("\nLast 3 Sell-side Sweeps")
print(sweeps["sell_side_sweeps"][-3:])

connector.disconnect()