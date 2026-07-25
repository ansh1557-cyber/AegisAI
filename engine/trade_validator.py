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
        fvg = analysis["M15"]["fvg"]
        liquidity = analysis["M15"]["liquidity"]
        premium_discount = analysis["M15"]["premium_discount"]
       
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
                
            # Bullish Fair Value Gap
            if len(fvg["bullish_fvg"]) > 0:
                checks.append("✅ Bullish Fair Value Gap")
            else:
                approved = False
                checks.append("❌ No Bullish Fair Value Gap")
            
            # Sell-side Liquidity Sweep
            if len(liquidity["sell_side_sweeps"]) > 0:
                checks.append("✅ Sell-side Liquidity Sweep")
            else:
                approved = False
                checks.append("❌ No Sell-side Liquidity Sweep")
            # Discount Zone
            if premium_discount["current_zone"] == "Discount":
                checks.append("✅ Discount Zone")
            else:
                approved = False
                checks.append("❌ Not in Discount Zone")

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
                
            # Bearish Fair Value Gap
            if len(fvg["bearish_fvg"]) > 0:
                checks.append("✅ Bearish Fair Value Gap")
            else:
                approved = False
                checks.append("❌ No Bearish Fair Value Gap")
            
            # Buy-side Liquidity Sweep
            if len(liquidity["buy_side_sweeps"]) > 0:
                checks.append("✅ Buy-side Liquidity Sweep")
            else:
                approved = False
                checks.append("❌ No Buy-side Liquidity Sweep")
            
            # Premium Zone
            if premium_discount["current_zone"] == "Premium":
                checks.append("✅ Premium Zone")
            else:
                approved = False
                checks.append("❌ Not in Premium Zone")

        return {
            "approved": approved,
            "checks": checks,
        }