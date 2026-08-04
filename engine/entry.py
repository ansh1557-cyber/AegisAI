"""
Aegis AI
Module: Entry Engine
Version: 0.2.0
"""


class EntryEngine:

    def analyze(self, analysis):

        bias = analysis["bias"]

        signal = {
            "signal": "WAIT",
            "confidence": bias["confidence"],
            "buy_reasons": bias["buy_reasons"],
            "sell_reasons": bias["sell_reasons"],
            "reasons": bias["buy_reasons"] + bias["sell_reasons"],
        }

        if bias["bias"] == "BUY":
            signal["signal"] = "BUY"

        elif bias["bias"] == "SELL":
            signal["signal"] = "SELL"

        return signal