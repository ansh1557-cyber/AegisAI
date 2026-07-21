from engine.mt5_connector import MT5Connector
from engine.market_structure import MarketStructureEngine

connector = MT5Connector()
connector.connect()

df = connector.get_rates(symbol="XAUUSD", bars=500)

engine = MarketStructureEngine()

result = engine.detect_swings(df)

print("Trend:", result["trend"])
print("Swing Highs:", len(result["swing_highs"]))
print("Swing Lows:", len(result["swing_lows"]))

connector.disconnect()