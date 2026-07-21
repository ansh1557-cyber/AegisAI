"""
Aegis AI
Example: Market Analyzer
Version: 0.3.1
"""

from engine.data_loader import DataLoader
from engine.market_structure import MarketStructureEngine
from engine.structure_analyzer import StructureAnalyzer

loader = DataLoader()

df = loader.load_csv("data/xauusd_m15.csv")

market = MarketStructureEngine()
result = market.detect_swings(df)

analyzer = StructureAnalyzer()
structure = analyzer.analyze(
    result["swing_highs"],
    result["swing_lows"]
)

print("=" * 50)
print("Aegis AI Market Analysis")
print("=" * 50)

print(f"Trend: {structure['trend']}")
print()

print(f"Swing Highs: {len(result['swing_highs'])}")
print(f"Swing Lows : {len(result['swing_lows'])}")

print()
print("Last 10 Swing Highs")
print(result["swing_highs"][-10:])

print()
print("Last 10 Swing Lows")
print(result["swing_lows"][-10:])

print()
print("Higher Highs:", len(structure["higher_highs"]))
print("Higher Lows :", len(structure["higher_lows"]))
print("Lower Highs :", len(structure["lower_highs"]))
print("Lower Lows  :", len(structure["lower_lows"]))