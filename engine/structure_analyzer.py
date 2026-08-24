"""
Aegis AI
Module: Structure Analyzer
Version: 0.2.0
"""

class StructureAnalyzer:

    def __init__(self):

        self.higher_highs = []
        self.higher_lows = []

        self.lower_highs = []
        self.lower_lows = []

        self.trend = "Unknown"

    # =====================================================
    # COMPARE HIGHS
    # =====================================================

    def compare_highs(self, swing_highs):

        self.higher_highs = []
        self.lower_highs = []

        if len(swing_highs) < 2:
            return

        for i in range(1, len(swing_highs)):

            previous = swing_highs[i - 1]
            current = swing_highs[i]

            if current[1] > previous[1]:

                self.higher_highs.append(
                    current
                )

            elif current[1] < previous[1]:

                self.lower_highs.append(
                    current
                )

    # =====================================================
    # COMPARE LOWS
    # =====================================================

    def compare_lows(self, swing_lows):

        self.higher_lows = []
        self.lower_lows = []

        if len(swing_lows) < 2:
            return

        for i in range(1, len(swing_lows)):

            previous = swing_lows[i - 1]
            current = swing_lows[i]

            if current[1] > previous[1]:

                self.higher_lows.append(
                    current
                )

            elif current[1] < previous[1]:

                self.lower_lows.append(
                    current
                )

    # =====================================================
    # DETECT TREND
    # =====================================================

    def detect_trend(
        self,
        swing_highs,
        swing_lows,
    ):

        if (
            len(swing_highs) < 2
            or len(swing_lows) < 2
        ):

            self.trend = "Range"

            return

        previous_high = swing_highs[-2][1]
        latest_high = swing_highs[-1][1]

        previous_low = swing_lows[-2][1]
        latest_low = swing_lows[-1][1]

        # -----------------------------------------
        # Bullish structure
        # -----------------------------------------

        if (
            latest_high > previous_high
            and latest_low > previous_low
        ):

            self.trend = "Bullish"

        # -----------------------------------------
        # Bearish structure
        # -----------------------------------------

        elif (
            latest_high < previous_high
            and latest_low < previous_low
        ):

            self.trend = "Bearish"

        # -----------------------------------------
        # Mixed / ranging structure
        # -----------------------------------------

        else:

            self.trend = "Range"

    # =====================================================
    # ANALYZE
    # =====================================================

    def analyze(
        self,
        swing_highs,
        swing_lows,
    ):

        self.compare_highs(
            swing_highs
        )

        self.compare_lows(
            swing_lows
        )

        self.detect_trend(
            swing_highs,
            swing_lows,
        )

        return {
            "trend": self.trend,

            "higher_highs":
                self.higher_highs,

            "higher_lows":
                self.higher_lows,

            "lower_highs":
                self.lower_highs,

            "lower_lows":
                self.lower_lows,
        }