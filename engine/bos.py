"""
Aegis AI
Module: Break of Structure (BOS) Engine
Version: 0.2.1
"""


class BOSEngine:

    def __init__(self):
        self.bullish_bos = False
        self.bearish_bos = False
        self.broken_level = None

    def detect(self, trend, swing_highs, swing_lows, df):
        """
        Detect Break of Structure (BOS)
        using candle body close.
        """

        # Reset
        self.bullish_bos = False
        self.bearish_bos = False
        self.broken_level = None

        if len(df) == 0:
            return self._result()

        last_close = df["Close"].iloc[-1]

        # Bullish BOS
        if trend == "Bullish" and swing_highs:

            last_swing_high = swing_highs[-1][1]

            if last_close > last_swing_high:
                self.bullish_bos = True
                self.broken_level = last_swing_high

        # Bearish BOS
        elif trend == "Bearish" and swing_lows:

            last_swing_low = swing_lows[-1][1]

            if last_close < last_swing_low:
                self.bearish_bos = True
                self.broken_level = last_swing_low

        return self._result()

    def _result(self):
        return {
            "bullish_bos": self.bullish_bos,
            "bearish_bos": self.bearish_bos,
            "broken_level": self.broken_level,
        }