"""
Aegis AI
Test: Market Structure Engine
Version: 0.0.1
"""

import pandas as pd

from engine.market_structure import MarketStructureEngine


# Sample OHLC Data
data = {
    "Open":  [100, 101, 102, 103, 104, 103, 102, 101, 100],
    "High":  [101, 102, 103, 105, 104, 103, 102, 101, 100],
    "Low":   [99, 100, 101, 102, 101, 100, 99, 98, 97],
    "Close": [100, 101, 102, 104, 103, 102, 101, 100, 99],
}

df = pd.DataFrame(data)

engine = MarketStructureEngine()

result = engine.detect_swings(df)

print("Swing Highs:", result["swing_highs"])
print("Swing Lows:", result["swing_lows"])
print("Trend:", result["trend"])
print("Higher Highs:", result["higher_highs"])
print("Higher Lows:", result["higher_lows"])
print("Lower Highs:", result["lower_highs"])
print("Lower Lows:", result["lower_lows"])