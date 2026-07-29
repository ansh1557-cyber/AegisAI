"""
Aegis AI
Module: Risk Manager
Version: 0.3.1
"""

from engine.symbol_info import SymbolInfo

from engine.config import (
    ACCOUNT_BALANCE,
    RISK_PERCENT,
    RISK_REWARD,
    SL_BUFFER,
)


class RiskManager:


    def __init__(self):

        self.symbol = SymbolInfo()



    def calculate(
        self,
        analysis,
        signal,
        entry_price,
        account_balance=ACCOUNT_BALANCE,
        risk_percent=RISK_PERCENT,
        rr=RISK_REWARD,
        buffer=SL_BUFFER,
    ):


        if signal["signal"] == "WAIT":

            return None



        risk_amount = account_balance * (
            risk_percent / 100
        )



        m15 = analysis["M15"]

        swings = m15["swings"]


        swing_lows = swings["swing_lows"]

        swing_highs = swings["swing_highs"]



        if not swing_lows or not swing_highs:

            return None



        latest_swing_low = swing_lows[-1][1]

        latest_swing_high = swing_highs[-1][1]



        # ==========================
        # BUY
        # ==========================

        if signal["signal"] == "BUY":


            stop_loss = latest_swing_low - buffer


            if stop_loss >= entry_price:

                stop_loss = entry_price - buffer



            sl_distance = entry_price - stop_loss


            take_profit = (
                entry_price +
                sl_distance * rr
            )



        # ==========================
        # SELL
        # ==========================

        else:


            stop_loss = latest_swing_high + buffer


            if stop_loss <= entry_price:

                stop_loss = entry_price + buffer



            sl_distance = stop_loss - entry_price


            take_profit = (
                entry_price -
                sl_distance * rr
            )



        sl_distance = abs(
            entry_price - stop_loss
        )



        if sl_distance <= 0:

            return None



        info = self.symbol.get()


        tick_value = info["tick_value"]

        tick_size = info["tick_size"]

        min_lot = info["min_lot"]

        max_lot = info["max_lot"]

        lot_step = info["lot_step"]



        # ==========================
        # LOT CALCULATION
        # ==========================


        lot_size = (
            risk_amount /
            (
                (sl_distance / tick_size)
                *
                tick_value
            )
        )



        lot_size = round(
            lot_size / lot_step
        ) * lot_step



        # ==========================
        # ACCOUNT SAFETY LIMIT
        # ==========================


        if account_balance < 200:

            lot_size = min(
                lot_size,
                0.01
            )


        elif account_balance < 500:

            lot_size = min(
                lot_size,
                0.02
            )



        lot_size = max(
            min_lot,
            lot_size
        )


        lot_size = min(
            max_lot,
            lot_size
        )



        return {


            "entry": round(entry_price, 2),

            "stop_loss": round(stop_loss, 2),

            "take_profit": round(take_profit, 2),

            "risk_reward": f"1:{rr}",

            "lot_size": round(lot_size, 2),

            "risk": round(risk_amount, 2),

        }