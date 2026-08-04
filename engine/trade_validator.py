"""
Aegis AI
Module: Trade Validator
Version: 1.0.0
"""


class TradeValidator:

    def validate(self, analysis, signal):

        checks = []

        hard_pass = True
        score = 0

        # =============================
        # HARD RULES
        # =============================

        if signal["signal"] == "WAIT":
            hard_pass = False
            checks.append("❌ Signal = WAIT")
        else:
            checks.append(f"✅ Signal: {signal['signal']}")

        if signal["confidence"] >= 70:
            checks.append(f"✅ Confidence: {signal['confidence']}%")
        else:
            hard_pass = False
            checks.append(
                f"❌ Confidence too low ({signal['confidence']}%)"
            )

        h4_trend = analysis["H4"]["structure"]["trend"]
        h1_trend = analysis["H1"]["structure"]["trend"]

        order_blocks = analysis["M15"]["order_blocks"]
        fvg = analysis["M15"]["fvg"]
        liquidity = analysis["M15"]["liquidity"]
        premium_discount = analysis["M15"]["premium_discount"]

        # =============================
        # BUY
        # =============================

        if signal["signal"] == "BUY":

            if h4_trend == "Bullish":
                checks.append("✅ H4 Bullish")
            else:
                hard_pass = False
                checks.append("❌ H4 not Bullish")

            if h1_trend == "Bullish":
                checks.append("✅ H1 Bullish")
            else:
                hard_pass = False
                checks.append("❌ H1 not Bullish")

            # ----- Soft confirmations -----

            if len(order_blocks["bullish_blocks"]) > 0:
                score += 25
                checks.append("✅ Bullish Order Block")
            else:
                checks.append("⚠ No Bullish Order Block")

            if len(fvg["bullish_fvg"]) > 0:
                score += 20
                checks.append("✅ Bullish Fair Value Gap")
            else:
                checks.append("⚠ No Bullish Fair Value Gap")

            if len(liquidity["sell_side_sweeps"]) > 0:
                score += 25
                checks.append("✅ Sell-side Liquidity Sweep")
            else:
                checks.append("⚠ No Sell-side Liquidity Sweep")

            if premium_discount["current_zone"] == "Discount":
                score += 15
                checks.append("✅ Discount Zone")
            else:
                checks.append("⚠ Not in Discount Zone")

        # =============================
        # SELL
        # =============================

        elif signal["signal"] == "SELL":

            if h4_trend == "Bearish":
                checks.append("✅ H4 Bearish")
            else:
                hard_pass = False
                checks.append("❌ H4 not Bearish")

            if h1_trend == "Bearish":
                checks.append("✅ H1 Bearish")
            else:
                hard_pass = False
                checks.append("❌ H1 not Bearish")

            if len(order_blocks["bearish_blocks"]) > 0:
                score += 25
                checks.append("✅ Bearish Order Block")
            else:
                checks.append("⚠ No Bearish Order Block")

            if len(fvg["bearish_fvg"]) > 0:
                score += 20
                checks.append("✅ Bearish Fair Value Gap")
            else:
                checks.append("⚠ No Bearish Fair Value Gap")

            if len(liquidity["buy_side_sweeps"]) > 0:
                score += 25
                checks.append("✅ Buy-side Liquidity Sweep")
            else:
                checks.append("⚠ No Buy-side Liquidity Sweep")

            if premium_discount["current_zone"] == "Premium":
                score += 15
                checks.append("✅ Premium Zone")
            else:
                checks.append("⚠ Not in Premium Zone")

        # =============================
        # FINAL DECISION
        # =============================

        approved = hard_pass and score >= 50

        checks.append("")
        checks.append(f"Validation Score : {score}/85")

        if approved:
            checks.append("✅ Trade Approved")
        else:
            checks.append("❌ Trade Rejected")

        return {
            "approved": approved,
            "score": score,
            "checks": checks,
        }