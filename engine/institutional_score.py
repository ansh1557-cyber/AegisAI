"""
Aegis AI
Module: Institutional Score Engine
Version: 1.0.0
"""


class InstitutionalScore:

    def __init__(self):

        self.buy_score = 0
        self.sell_score = 0

        self.buy_reasons = []
        self.sell_reasons = []

    # ==========================
    # BUY
    # ==========================

    def add_buy(self, points, reason):

        self.buy_score += points
        self.buy_reasons.append(f"+{points} {reason}")

    # ==========================
    # SELL
    # ==========================

    def add_sell(self, points, reason):

        self.sell_score += points
        self.sell_reasons.append(f"+{points} {reason}")

    # ==========================
    # RESULT
    # ==========================

    def result(self):

        maximum_score = 120

        if self.buy_score > self.sell_score:

            signal = "BUY"
            confidence = round((self.buy_score / maximum_score) * 100)

        elif self.sell_score > self.buy_score:

            signal = "SELL"
            confidence = round((self.sell_score / maximum_score) * 100)

        else:

            signal = "WAIT"
            confidence = 0

        return {
            "buy_score": self.buy_score,
            "sell_score": self.sell_score,
            "buy_reasons": self.buy_reasons,
            "sell_reasons": self.sell_reasons,
            "signal": signal,
            "confidence": confidence,
        }

    # ==========================
    # PRINT
    # ==========================

    def print_result(self):

        result = self.result()

        print("\n========== INSTITUTIONAL SCORE ==========\n")

        print("BUY SCORE\n")

        if result["buy_reasons"]:

            for reason in result["buy_reasons"]:
                print(reason)

        else:
            print("No bullish evidence")

        print(f"\nBUY TOTAL : {result['buy_score']}")

        print("\n------------------------------\n")

        print("SELL SCORE\n")

        if result["sell_reasons"]:

            for reason in result["sell_reasons"]:
                print(reason)

        else:
            print("No bearish evidence")

        print(f"\nSELL TOTAL : {result['sell_score']}")

        print("\n==============================")

        print(f"Signal      : {result['signal']}")
        print(f"Confidence  : {result['confidence']}%")

        return result