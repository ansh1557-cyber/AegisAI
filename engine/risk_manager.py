"""
Aegis AI
Module: Risk Manager
Version: 0.2.0
"""


class RiskManager:

    def calculate(
        self,
        signal,
        entry_price,
        account_balance=10000,
        risk_percent=1,
        rr=2,
        sl_points=50,
    ):

        if signal["signal"] == "WAIT":
            return None

        risk_amount = account_balance * (risk_percent / 100)

        if signal["signal"] == "BUY":

            stop_loss = entry_price - sl_points
            take_profit = entry_price + (sl_points * rr)

        else:

            stop_loss = entry_price + sl_points
            take_profit = entry_price - (sl_points * rr)

        return {

            "entry": round(entry_price, 2),

            "stop_loss": round(stop_loss, 2),

            "take_profit": round(take_profit, 2),

            "risk_reward": f"1:{rr}",

            "lot_size": 0.10,

            "risk": risk_amount,
        }