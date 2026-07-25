"""
Aegis AI
Module: Trade Validator
Version: 0.1.0
"""


class TradeValidator:

    def validate(self, analysis, signal):

        reasons = []

        approved = True

        # Signal check
        if signal["signal"] == "WAIT":
            approved = False
            reasons.append("Signal is WAIT")

        # Confidence check
        if signal["confidence"] < 70:
            approved = False
            reasons.append("Confidence below 70%")

        # H4 trend
        h4_trend = analysis["H4"]["structure"]["trend"]

        if signal["signal"] == "BUY" and h4_trend != "Bullish":
            approved = False
            reasons.append("H4 trend not Bullish")

        if signal["signal"] == "SELL" and h4_trend != "Bearish":
            approved = False
            reasons.append("H4 trend not Bearish")

        return {
            "approved": approved,
            "reasons": reasons,
        }