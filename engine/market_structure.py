"""
Aegis AI
Module: Market Structure Engine
Version: 0.0.2
"""

import pandas as pd


class MarketStructureEngine:

    def __init__(self):
        self.swing_highs = []
        self.swing_lows = []

        self.higher_highs=[]
        self.higher_lows=[]

        self.lower_highs=[]
        self.lower_lows=[]

        self.trend="Unknown"

    def detect_swings(self, df):

        self.swing_highs = []
        self.swing_lows = []

        for i in range(2, len(df) - 2):

            high = df["High"].iloc[i]
            low = df["Low"].iloc[i]

            # Swing High
            if (
                high > df["High"].iloc[i - 1]
                and high > df["High"].iloc[i - 2]
                and high > df["High"].iloc[i + 1]
                and high > df["High"].iloc[i + 2]
            ):
                self.swing_highs.append((i, high))

            # Swing Low
            if (
                low < df["Low"].iloc[i - 1]
                and low < df["Low"].iloc[i - 2]
                and low < df["Low"].iloc[i + 1]
                and low < df["Low"].iloc[i + 2]
            ):
                self.swing_lows.append((i, low))

        return {
            "trend":self.trend,
            "swing_highs": self.swing_highs,
            "swing_lows": self.swing_lows,
            "higher_highs":self.higher_highs,
            "higher_lows":self.higher_lows,
            "lower_highs":self.lower_highs,
            "lower_lows":self.lower_lows
        }