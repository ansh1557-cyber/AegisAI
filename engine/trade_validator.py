"""
Aegis AI
Module: Trade Validator
Version: 0.4.0
"""


class TradeValidator:

    def validate(self, analysis, signal):

        checks = []
        approved = True

        # -----------------------------
        # Signal Check
        # -----------------------------
        if signal["signal"] == "WAIT":
            approved = False
            checks.append("❌ Signal is WAIT")
        else:
            checks.append(f"✅ Signal: {signal['signal']}")

        # -----------------------------
        # Confidence Check
        # -----------------------------
        if signal["confidence"] >= 70:
            checks.append(f"✅ Confidence: {signal['confidence']}%")
        else:
            approved = False
            checks.append(f"❌ Confidence too low ({signal['confidence']}%)")

        # -----------------------------
        # Market Data
        # -----------------------------
        h4_trend = analysis["H4"]["structure"]["trend"]
        h1_trend = analysis["H1"]["structure"]["trend"]
        order_blocks = analysis["M15"]["order_blocks"]

        # -----------------------------
        # BUY Validation
        # -----------------------------
        if signal["signal"] == "BUY":

            # H4 Trend
            if h4_trend == "Bullish":
                checks.append("✅ H4 Bullish")
            else:
                approved = False
                checks.append("❌ H4 not Bullish")

            # H1 Trend
            if h1_trend == "Bullish":
                checks.append("✅ H1 Bullish")
            else:
                approved = False
                checks.append("❌ H1 not Bullish")

            # Bullish Order Block
            if len(order_blocks["bullish_blocks"]) > 0:
                checks.append("✅ Bullish Order Block")
            else:
                approved = False
                checks.append("❌ No Bullish Order Block")

        # -----------------------------
        # SELL Validation
        # -----------------------------
        elif signal["signal"] == "SELL":

            # H4 Trend
            if h4_trend == "Bearish":
                checks.append("✅ H4 Bearish")
            else:
                approved = False
                checks.append("❌ H4 not Bearish")

            # H1 Trend
            if h1_trend == "Bearish":
                checks.append("✅ H1 Bearish")
            else:
                approved = False
                checks.append("❌ H1 not Bearish")

            # Bearish Order Block
            if len(order_blocks["bearish_blocks"]) > 0:
                checks.append("✅ Bearish Order Block")
            else:
                approved = False
                checks.append("❌ No Bearish Order Block")

        return {
            "approved": approved,
            "checks": checks,
        }