"""
Aegis AI
Module: Liquidity Sweep Engine
Version: 0.3.2
"""


class LiquidityEngine:

    def __init__(self):
        self.buy_side_sweeps = []
        self.sell_side_sweeps = []

    def detect(self, df, swing_highs, swing_lows):

        self.buy_side_sweeps = []
        self.sell_side_sweeps = []

        # Buy-side liquidity
        for index, level in swing_highs:

            for i in range(index + 1, min(index + 21, len(df))):

                if (
                    df["high"].iloc[i] > level
                    and df["close"].iloc[i] < level
                ):

                    self.buy_side_sweeps.append(
                        {
                            "index": i,
                            "level": level,
                        }
                    )

                    break

        # Sell-side liquidity
        for index, level in swing_lows:

            for i in range(index + 1, min(index + 21, len(df))):

                if (
                    df["low"].iloc[i] < level
                    and df["close"].iloc[i] > level
                ):

                    self.sell_side_sweeps.append(
                        {
                            "index": i,
                            "level": level,
                        }
                    )

                    break

        return {
            "buy_side_sweeps": self.buy_side_sweeps,
            "sell_side_sweeps": self.sell_side_sweeps,
        }