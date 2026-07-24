from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.bias import BiasEngine
from engine.entry import EntryEngine

analysis = MultiTimeframeAnalyzer().analyze()

bias = BiasEngine().analyze(analysis)

results = {
    "analysis": analysis,
    "bias": bias,
}

signal = EntryEngine().analyze(results)

print("\n========== AEGIS AI ENTRY ==========\n")

print("Signal:", signal["signal"])
print("Confidence:", signal["confidence"])

print("\nReasons:")

for reason in signal["reasons"]:
    print("✓", reason)