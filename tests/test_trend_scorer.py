"""
Test Trend Scorer
"""

from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.scorers.trend import TrendScorer

print("\nAnalyzing market...\n")

analysis = MultiTimeframeAnalyzer().analyze()

result = TrendScorer().score(analysis)

print("\n========== TREND SCORE ==========\n")

print(f"Score : {result['score']}")

print("\nReasons:")

for reason in result["reasons"]:
    print("-", reason)