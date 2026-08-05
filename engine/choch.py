"""
Aegis AI
Module: Change of Character (CHoCH) Engine
Version: 0.3.0
"""


class CHOCHEngine:

    def __init__(self):
        self.bullish_choch = False
        self.bearish_choch = False
        self.broken_level = None

    def detect(self, trend, swing_highs, swing_lows, df):

        # Reset
        self.bullish_choch = False
        self.bearish_choch = False
        self.broken_level = None

        if len(df) == 0:
            return self._result()

        last_close = df["close"].iloc[-1]

        # Bullish CHoCH
        if trend == "Bearish" and swing_highs:

            last_swing_high = swing_highs[-1][1]

            if last_close > last_swing_high:
                self.bullish_choch = True
                self.broken_level = last_swing_high

        # Bearish CHoCH
        elif trend == "Bullish" and swing_lows:

            last_swing_low = swing_lows[-1][1]

            if last_close < last_swing_low:
                self.bearish_choch = True
                self.broken_level = last_swing_low

        return self._result()

    def _result(self):
        return {
            "bullish_choch": self.bullish_choch,
            "bearish_choch": self.bearish_choch,
            "broken_level": self.broken_level,
        }