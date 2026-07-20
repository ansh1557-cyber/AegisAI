"""
Aegis AI
Module: Market Structure Engine
Version: 0.0.3
"""

class MarketStructureEngine:

    def __init__(self):
        self.swing_highs = []
        self.swing_lows = []

        self.higher_highs = []
        self.higher_lows = []

        self.lower_highs = []
        self.lower_lows = []

        self.trend = "Unknown"

    def detect_swings(self, df, lookback=2):

        self.swing_highs = []
        self.swing_lows = []

        for i in range(lookback, len(df) - lookback):

            high = df["High"].iloc[i]
            low = df["Low"].iloc[i]

            left_high = df["High"].iloc[i - lookback:i]
            right_high = df["High"].iloc[i + 1:i + lookback + 1]

            left_low = df["Low"].iloc[i - lookback:i]
            right_low = df["Low"].iloc[i + 1:i + lookback + 1]

            # Swing High
            if high > max(left_high) and high > max(right_high):
                self.swing_highs.append((i, high))

            # Swing Low
            if low < min(left_low) and low < min(right_low):
                self.swing_lows.append((i, low))

        return {
            "trend": self.trend,
            "swing_highs": self.swing_highs,
            "swing_lows": self.swing_lows,
            "higher_highs": self.higher_highs,
            "higher_lows": self.higher_lows,
            "lower_highs": self.lower_highs,
            "lower_lows": self.lower_lows,
        }