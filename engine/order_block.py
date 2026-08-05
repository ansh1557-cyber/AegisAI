"""
Aegis AI
Module: Order Block Engine
Version: 0.4.0
"""


class OrderBlockEngine:

    def __init__(self):
        self.bullish_blocks = []
        self.bearish_blocks = []

    def detect(self, df):

        self.bullish_blocks = []
        self.bearish_blocks = []

        # Bullish Order Blocks
        for i in range(1, len(df) - 1):

            previous = df.iloc[i - 1]
            current = df.iloc[i]
            nxt = df.iloc[i + 1]

            # Last bearish candle before bullish expansion
            if (
                current["close"] < current["open"]
                and nxt["close"] > current["high"]
            ):

                self.bullish_blocks.append(
                    {
                        "index": i,
                        "high": current["high"],
                        "low": current["low"],
                    }
                )

            # Last bullish candle before bearish expansion
            if (
                current["close"] > current["open"]
                and nxt["close"] < current["low"]
            ):

                self.bearish_blocks.append(
                    {
                        "index": i,
                        "high": current["high"],
                        "low": current["low"],
                    }
                )

        return {
            "bullish_blocks": self.bullish_blocks,
            "bearish_blocks": self.bearish_blocks,
        }