"""
Aegis AI
Test: Market Bias Engine
Version: 0.5.0
"""

from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.bias import BiasEngine

multi = MultiTimeframeAnalyzer()
results = multi.analyze()
bias_engine = BiasEngine()

print(results["M15"]["order_blocks"])
print(results["M15"]["order_blocks"].keys())

print(results["M15"]["fvg"])
print(results["M15"]["fvg"].keys())

bias = bias_engine.analyze(results)

print("\n========== AEGIS AI MARKET BIAS ==========\n")

print("Bias:", bias["bias"])
print("Confidence:", f'{bias["confidence"]}%')
print("Score:", bias["score"])

print("\nReasons:")

for reason in bias["reasons"]:
    print(f"✓ {reason}")