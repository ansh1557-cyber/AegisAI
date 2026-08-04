"""
Aegis AI
Module: Market Bias Engine
Version: 1.0.0
"""


class BiasEngine:

    def analyze(self, results):

        buy_score = 0
        sell_score = 0

        buy_reasons = []
        sell_reasons = []

        # ==========================================
        # H4 ANALYSIS
        # ==========================================

        h4 = results["H4"]

        trend = h4["structure"]["trend"]

        if trend == "Bullish":
            buy_score += 30
            buy_reasons.append("H4 Bullish Trend")

        elif trend == "Bearish":
            sell_score += 30
            sell_reasons.append("H4 Bearish Trend")

        zone = h4["premium_discount"]["current_zone"]

        if zone == "Discount":
            buy_score += 10
            buy_reasons.append("Discount Zone")

        elif zone == "Premium":
            sell_score += 10
            sell_reasons.append("Premium Zone")

        # ==========================================
        # H1 ANALYSIS
        # ==========================================

        h1 = results["H1"]

        trend = h1["structure"]["trend"]

        if trend == "Bullish":
            buy_score += 20
            buy_reasons.append("H1 Bullish Trend")

        elif trend == "Bearish":
            sell_score += 20
            sell_reasons.append("H1 Bearish Trend")

        if h1["bos"]["bullish_bos"]:
            buy_score += 15
            buy_reasons.append("Bullish BOS")

        if h1["bos"]["bearish_bos"]:
            sell_score += 15
            sell_reasons.append("Bearish BOS")

        if h1["choch"]["bullish_choch"]:
            buy_score += 10
            buy_reasons.append("Bullish CHoCH")

        if h1["choch"]["bearish_choch"]:
            sell_score += 10
            sell_reasons.append("Bearish CHoCH")

        # ==========================================
        # M15 ANALYSIS
        # ==========================================

        m15 = results["M15"]

        bullish_blocks = len(m15["order_blocks"]["bullish_blocks"])
        bearish_blocks = len(m15["order_blocks"]["bearish_blocks"])

        if bullish_blocks > 0:
            buy_score += 10
            buy_reasons.append(f"{bullish_blocks} Bullish Order Blocks")

        if bearish_blocks > 0:
            sell_score += 10
            sell_reasons.append(f"{bearish_blocks} Bearish Order Blocks")

        bullish_fvg = len(m15["fvg"]["bullish_fvg"])
        bearish_fvg = len(m15["fvg"]["bearish_fvg"])

        if bullish_fvg > 0:
            buy_score += 10
            buy_reasons.append(f"{bullish_fvg} Bullish FVG")

        if bearish_fvg > 0:
            sell_score += 10
            sell_reasons.append(f"{bearish_fvg} Bearish FVG")

        # ==========================================
        # FINAL DECISION
        # ==========================================

        if buy_score > sell_score:
            signal = "BUY"

        elif sell_score > buy_score:
            signal = "SELL"

        else:
            signal = "NEUTRAL"

        total = buy_score + sell_score

        if total == 0:
            confidence = 0
        else:
            confidence = int(max(buy_score, sell_score) / total * 100)

        score = buy_score - sell_score

        return {
            "bias": signal,
            "signal": signal,
            "confidence": confidence,
            "score": score,
            "buy_score": buy_score,
            "sell_score": sell_score,
            "buy_reasons": buy_reasons,
            "sell_reasons": sell_reasons,
        }