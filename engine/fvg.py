"""
Aegis AI
Module: Fair Value Gap (FVG) Engine
Version: 0.3.1
"""

class FVGEngine:

    def detect(self, df):
        bullish_fvg = []
        bearish_fvg = []

        for i in range(1, len(df) - 1):
            c1 = df.iloc[i - 1]
            c2 = df.iloc[i]
            c3 = df.iloc[i + 1]

            # Bullish FVG
            if c1["high"] < c3["low"]:
                bullish_fvg.append({
                    "index": i,
                    "top": c3["low"],
                    "bottom": c1["high"],
                })

            # Bearish FVG
            if c1["low"] > c3["high"]:
                bearish_fvg.append({
                    "index": i,
                    "top": c1["low"],
                    "bottom": c3["high"],
                })

        return {
            "bullish_fvg": bullish_fvg,
            "bearish_fvg": bearish_fvg,
        }