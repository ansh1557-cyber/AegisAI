"""
Aegis AI
Module: Premium / Discount Zone Engine
Version: 0.4.1
"""


class PremiumDiscountEngine:

    def detect(self, df, swing_highs, swing_lows):

        if not swing_highs or not swing_lows:
            return {
                "premium": None,
                "discount": None,
                "equilibrium": None,
                "current_zone": "Unknown",
            }

        highest = max(level for _, level in swing_highs)
        lowest = min(level for _, level in swing_lows)

        equilibrium = (highest + lowest) / 2

        current_price = df["Close"].iloc[-1]

        if current_price > equilibrium:
            zone = "Premium"
        elif current_price < equilibrium:
            zone = "Discount"
        else:
            zone = "Equilibrium"

        return {
            "premium": highest,
            "discount": lowest,
            "equilibrium": equilibrium,
            "current_zone": zone,
        }