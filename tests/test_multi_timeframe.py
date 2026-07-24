"""
Aegis AI
Test: Multi-Timeframe Analyzer
Version: 0.5.0
"""

from engine.multi_timeframe import MultiTimeframeAnalyzer

analyzer = MultiTimeframeAnalyzer()

results = analyzer.analyze()

print("\n========== MULTI-TIMEFRAME ANALYSIS ==========\n")

for timeframe, result in results.items():

    print(f"----- {timeframe} -----")

    print("Trend:",
          result["structure"]["trend"])

    print("Bullish BOS:",
          result["bos"]["bullish_bos"])

    print("Bearish BOS:",
          result["bos"]["bearish_bos"])

    print("Bullish CHoCH:",
          result["choch"]["bullish_choch"])

    print("Bearish CHoCH:",
          result["choch"]["bearish_choch"])

    print("Current Zone:",
          result["premium_discount"]["current_zone"])

    print()