"""
Aegis AI
Test: Market Structure Engine
Version: 0.0.1
"""
from engine.structure_analyzer import StructureAnalyzer
from engine.data_loader import DataLoader
from engine.market_structure import MarketStructureEngine


loader = DataLoader()
df = loader.load_csv("data/sample_data.csv")

engine = MarketStructureEngine()

result = engine.detect_swings(df)

analyzer = StructureAnalyzer()

structure = analyzer.analyze(
    result["swing_highs"],
    result["swing_lows"]
)

print("Swing Highs:", result["swing_highs"])
print("Swing Lows:", result["swing_lows"])
print("Trend:", structure["trend"])
print("Higher Highs:", structure["higher_highs"])
print("Higher Lows:", structure["higher_lows"])
print("Lower Highs:", structure["lower_highs"])
print("Lower Lows:", structure["lower_lows"])