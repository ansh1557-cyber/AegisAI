"""
Aegis AI
Module: Structure Analyzer
Version: 0.1.2
"""


class StructureAnalyzer:

    def __init__(self):
        self.higher_highs = []
        self.higher_lows = []
        self.lower_highs = []
        self.lower_lows = []
        self.trend = "Unknown"

    def compare_highs(self, swing_highs):
        """
        Compare consecutive swing highs and classify them
        as Higher High (HH) or Lower High (LH).
        """

        self.higher_highs = []
        self.lower_highs = []

        if len(swing_highs) < 2:
            return

        for i in range(1, len(swing_highs)):
            previous = swing_highs[i - 1]
            current = swing_highs[i]

            if current[1] > previous[1]:
                self.higher_highs.append(current)
            elif current[1] < previous[1]:
                self.lower_highs.append(current)

    def compare_lows(self, swing_lows):
        """
        Compare consecutive swing lows and classify them
        as Higher Low (HL) or Lower Low (LL).
        """

        self.higher_lows = []
        self.lower_lows = []

        if len(swing_lows) < 2:
            return

        for i in range(1, len(swing_lows)):
            previous = swing_lows[i - 1]
            current = swing_lows[i]

            if current[1] > previous[1]:
                self.higher_lows.append(current)
            elif current[1] < previous[1]:
                self.lower_lows.append(current)

    def detect_trend(self):
        """
        Detect the overall market trend.
        """

        if self.higher_highs and self.higher_lows:
            self.trend = "Bullish"

        elif self.lower_highs and self.lower_lows:
            self.trend = "Bearish"

        else:
            self.trend = "Range"

    def analyze(self, swing_highs, swing_lows):

        self.compare_highs(swing_highs)
        self.compare_lows(swing_lows)
        self.detect_trend()

        return {
            "trend": self.trend,
            "higher_highs": self.higher_highs,
            "higher_lows": self.higher_lows,
            "lower_highs": self.lower_highs,
            "lower_lows": self.lower_lows,
        }