"""
Aegis AI
Module: Entry Engine
Version: 0.1.0
"""


class EntryEngine:

    def analyze(self, analysis):

        bias = analysis["bias"]

        signal = {
            "signal": "WAIT",
            "confidence": bias["confidence"],
            "reasons": bias["reasons"],
        }

        if bias["bias"] == "STRONG BUY":
            signal["signal"] = "BUY"

        elif bias["bias"] == "STRONG SELL":
            signal["signal"] = "SELL"

        return signal