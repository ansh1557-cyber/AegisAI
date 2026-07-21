"""
Aegis AI
Test: BOS Engine
Version: 0.2.1
"""

from engine.data_loader import DataLoader
from engine.market_structure import MarketStructureEngine
from engine.structure_analyzer import StructureAnalyzer
from engine.bos import BOSEngine

loader = DataLoader()
df = loader.load_csv("data/test_cases/bullish_bos.csv")

market = MarketStructureEngine()
result = market.detect_swings(df)

analyzer = StructureAnalyzer()
structure = analyzer.analyze(
    result["swing_highs"],
    result["swing_lows"]
)

bos = BOSEngine()
bos_result = bos.detect(
    structure["trend"],
    result["swing_highs"],
    result["swing_lows"],
    df
)

print("Trend:", structure["trend"])
print("Bullish BOS:", bos_result["bullish_bos"])
print("Bearish BOS:", bos_result["bearish_bos"])
print("Broken Level:", bos_result["broken_level"])