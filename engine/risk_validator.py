"""
Aegis AI
Module: Risk Validator
Version: 0.1.0
"""


class RiskValidator:


    def validate(self, signal, trade):


        checks = []

        approved = True


        if signal["signal"] == "WAIT":

            return {
                "approved": False,
                "checks": ["❌ No trade signal"]
            }



        entry = trade["entry"]
        stop_loss = trade["stop_loss"]
        take_profit = trade["take_profit"]



        # ==========================
        # BUY VALIDATION
        # ==========================

        if signal["signal"] == "BUY":


            if stop_loss < entry:

                checks.append(
                    "✅ BUY SL below entry"
                )

            else:

                checks.append(
                    "❌ BUY SL must be below entry"
                )

                approved = False



            if take_profit > entry:

                checks.append(
                    "✅ BUY TP above entry"
                )

            else:

                checks.append(
                    "❌ BUY TP must be above entry"
                )

                approved = False



        # ==========================
        # SELL VALIDATION
        # ==========================

        elif signal["signal"] == "SELL":


            if stop_loss > entry:

                checks.append(
                    "✅ SELL SL above entry"
                )

            else:

                checks.append(
                    "❌ SELL SL must be above entry"
                )

                approved = False



            if take_profit < entry:

                checks.append(
                    "✅ SELL TP below entry"
                )

            else:

                checks.append(
                    "❌ SELL TP must be below entry"
                )

                approved = False



        # ==========================
        # RISK REWARD CHECK
        # ==========================

        risk = abs(entry - stop_loss)

        reward = abs(take_profit - entry)


        if risk == 0:

            checks.append(
                "❌ Zero stop loss distance"
            )

            approved = False


        else:

            rr = reward / risk


            if rr >= 1:

                checks.append(
                    f"✅ Risk Reward acceptable: 1:{round(rr,2)}"
                )

            else:

                checks.append(
                    f"❌ Poor Risk Reward: 1:{round(rr,2)}"
                )

                approved = False



        return {

            "approved": approved,

            "checks": checks

        }