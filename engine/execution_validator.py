"""
Aegis AI
Module: Execution Validator
Version: 0.1.0
"""

from engine.symbol_info import SymbolInfo
import MetaTrader5 as mt5

class ExecutionValidator:

    def __init__(self):
        self.symbol = SymbolInfo()


    def validate(self, request):

        info = self.symbol.get()

        checks = []


        # ==========================
        # LOT CHECK
        # ==========================

        volume = request["volume"]

        if volume < info["min_lot"]:
            checks.append(
                "❌ Lot size below minimum"
            )

        elif volume > info["max_lot"]:
            checks.append(
                "❌ Lot size above maximum"
            )

        else:
            checks.append(
                "✅ Lot size valid"
            )


        # ==========================
        # SPREAD CHECK
        # ==========================

        spread = info["spread"]

        if spread > 100:
            checks.append(
                "❌ Spread too high"
            )

        else:
            checks.append(
                "✅ Spread acceptable"
            )


        # ==========================
        # SL / TP DIRECTION CHECK
        # ==========================

        if "type" in request:

            entry = request["price"]
            sl = request["sl"]
            tp = request["tp"]


            # BUY
            if request["type"] == mt5.ORDER_TYPE_BUY:

                if sl < entry and tp > entry:
                    checks.append(
                        "✅ BUY SL/TP valid"
                    )

                else:
                    checks.append(
                        "❌ BUY SL/TP invalid"
                    )


            # SELL
            else:

                if sl > entry and tp < entry:
                    checks.append(
                        "✅ SELL SL/TP valid"
                    )

                else:
                    checks.append(
                        "❌ SELL SL/TP invalid"
                    )


        approved = all(
            "❌" not in check
            for check in checks
        )


        return {
            "approved": approved,
            "checks": checks,
        }