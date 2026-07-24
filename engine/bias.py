"""
Aegis AI
Module: Market Bias Engine
Version: 0.5.0
"""


class BiasEngine:

    def analyze(self, results):
        
        
        score = 0
        reasons = []

        # -------------------------
        # H4 (Highest Priority)
        # -------------------------

        h4 = results["H4"]

        if h4["structure"]["trend"] == "Bullish":
            score += 3
            reasons.append("H4 Bullish Trend")
        elif h4["structure"]["trend"] == "Bearish":
            score -= 3
            reasons.append("H4 Bearish Trend")

        if h4["premium_discount"]["current_zone"] == "Discount":
            score += 2
            reasons.append("H4 Discount Zone")
        else:
            score -= 1
            reasons.append("H4 Premium Zone")

        # -------------------------
        # H1
        # -------------------------

        h1 = results["H1"]

        if h1["bos"]["bullish_bos"]:
            score += 2
            reasons.append("H1 Bullish BOS")

        if h1["bos"]["bearish_bos"]:
            score -= 2
            reasons.append("H1 Bearish BOS")

        if h1["choch"]["bullish_choch"]:
            score += 1
            reasons.append("H1 Bullish CHoCH")

        if h1["choch"]["bearish_choch"]:
            score -= 1
            reasons.append("H1 Bearish CHoCH")

        # -------------------------
        # M15
        # -------------------------

        m15 = results["M15"]

        if len(m15["order_blocks"]["bullish_blocks"]) > 0:
           score += 1
           reasons.append("Bullish Order Block")

        if len(m15["fvg"]["bullish_fvg"]) > 0:
            score += 1
            reasons.append("Bullish Fair Value Gap")

        # -------------------------
        # Final Decision
        # -------------------------

        if score >= 5:
            bias = "STRONG BUY"

        elif score >= 2:
            bias = "BUY"

        elif score <= -5:
            bias = "STRONG SELL"

        elif score <= -2:
            bias = "SELL"

        else:
            bias = "NEUTRAL"

        confidence = min(abs(score) * 10, 100)

        return {
            "bias": bias,
            "confidence": confidence,
            "score": score,
            "reasons": reasons,
        }