"""
Aegis AI
Module: Trade Validator
Version: 0.3.0
"""


class TradeValidator:

    def validate(self, analysis, signal):

        checks = []
        approved = True

        # Signal
        if signal["signal"] == "WAIT":
            approved = False
            checks.append("❌ Signal is WAIT")
        else:
            checks.append(f"✅ Signal: {signal['signal']}")

        # Confidence
        if signal["confidence"] >= 70:
            checks.append(f"✅ Confidence: {signal['confidence']}%")
        else:
            approved = False
            checks.append(f"❌ Confidence too low ({signal['confidence']}%)")

        # H4
        h4_trend = analysis["H4"]["structure"]["trend"]

        # H1
        h1_trend = analysis["H1"]["structure"]["trend"]

        if signal["signal"] == "BUY":

            if h4_trend == "Bullish":
                checks.append("✅ H4 Bullish")
            else:
                approved = False
                checks.append("❌ H4 not Bullish")

            if h1_trend == "Bullish":
                checks.append("✅ H1 Bullish")
            else:
                approved = False
                checks.append("❌ H1 not Bullish")

        elif signal["signal"] == "SELL":

            if h4_trend == "Bearish":
                checks.append("✅ H4 Bearish")
            else:
                approved = False
                checks.append("❌ H4 not Bearish")

            if h1_trend == "Bearish":
                checks.append("✅ H1 Bearish")
            else:
                approved = False
                checks.append("❌ H1 not Bearish")

        return {
            "approved": approved,
            "checks": checks,
        }