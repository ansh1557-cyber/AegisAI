"""
Aegis AI
Test: Market Structure Engine
Version: 0.0.1
"""
from engine.structure_analyzer import StructureAnalyzer
from engine.data_loader import DataLoader
from engine.market_structure import MarketStructureEngine
from engine.bos import BOSEngine
from engine.choch import CHOCHEngine


loader = DataLoader()
df = loader.load_csv("data/test_cases/bullish_trend.csv")

engine = MarketStructureEngine()

result = engine.detect_swings(df)

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

choch = CHOCHEngine()

choch_result = choch.detect(
    structure["trend"],
    result["swing_highs"],
    result["swing_lows"],
    df
)

print("Swing Highs:", result["swing_highs"])
print("Swing Lows:", result["swing_lows"])
print("Trend:", structure["trend"])
print("Higher Highs:", structure["higher_highs"])
print("Higher Lows:", structure["higher_lows"])
print("Lower Highs:", structure["lower_highs"])
print("Lower Lows:", structure["lower_lows"])
print("Bullish BOS:", bos_result["bullish_bos"])
print("Bearish BOS:", bos_result["bearish_bos"])
print("Broken Level:", bos_result["broken_level"])
print("Bullish CHoCH:", choch_result["bullish_choch"])
print("Bearish CHoCH:", choch_result["bearish_choch"])
print("Broken Level:", choch_result["broken_level"])