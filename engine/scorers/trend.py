"""
Aegis AI
Module: Trend Scorer
Version: 1.0.0
"""


class TrendScorer:
    """
    Scores the higher-timeframe trend.
    """

    H4_WEIGHT = 30
    H1_WEIGHT = 20

    def score(self, analysis):

        score = 0
        reasons = []

        # --------------------------
        # H4 Trend
        # --------------------------

        h4 = analysis["H4"]["structure"]["trend"]

        if h4 == "Bullish":
            score += self.H4_WEIGHT
            reasons.append(f"H4 Bullish (+{self.H4_WEIGHT})")

        elif h4 == "Bearish":
            score -= self.H4_WEIGHT
            reasons.append(f"H4 Bearish (-{self.H4_WEIGHT})")

        else:
            reasons.append("H4 Range (+0)")

        # --------------------------
        # H1 Trend
        # --------------------------

        h1 = analysis["H1"]["structure"]["trend"]

        if h1 == "Bullish":
            score += self.H1_WEIGHT
            reasons.append(f"H1 Bullish (+{self.H1_WEIGHT})")

        elif h1 == "Bearish":
            score -= self.H1_WEIGHT
            reasons.append(f"H1 Bearish (-{self.H1_WEIGHT})")

        else:
            reasons.append("H1 Range (+0)")

        return {
            "score": score,
            "reasons": reasons,
        }