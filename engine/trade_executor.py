"""
Aegis AI
Module: Trade Executor
Version: 0.4.0
"""

from datetime import datetime

import MetaTrader5 as mt5

from engine.config import SYMBOL, DRY_RUN, MAGIC_NUMBER
from engine.database import Database


class TradeExecutor:

    def __init__(self):

        self.db = Database()


    def has_open_trade(self, signal):

        positions = mt5.positions_get(symbol=SYMBOL)

        if positions is None:
            return False


        desired_type = (
            mt5.ORDER_TYPE_BUY
            if signal["signal"] == "BUY"
            else mt5.ORDER_TYPE_SELL
        )


        for position in positions:

            if (
                position.magic == MAGIC_NUMBER
                and position.type == desired_type
            ):
                return True


        return False



    def build_order(self, signal, trade):

        if signal["signal"] == "WAIT":
            return None


        tick = mt5.symbol_info_tick(SYMBOL)

        if tick is None:
            raise Exception(
                f"Unable to get price for {SYMBOL}"
            )


        if signal["signal"] == "BUY":

            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask

        else:

            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid



        request = {

            "action": mt5.TRADE_ACTION_DEAL,

            "symbol": SYMBOL,

            "volume": trade["lot_size"],

            "type": order_type,

            "price": price,

            "sl": trade["stop_loss"],

            "tp": trade["take_profit"],

            "deviation": 20,

            "magic": MAGIC_NUMBER,

            "comment": "Aegis AI",

            "type_time": mt5.ORDER_TIME_GTC,

            "type_filling": mt5.ORDER_FILLING_IOC,

        }


        print("\n========== ORDER DEBUG ==========\n")

        print(f"Symbol : {SYMBOL}")
        print(
            f"Type   : {'BUY' if order_type == mt5.ORDER_TYPE_BUY else 'SELL'}"
        )
        print(f"Entry  : {price}")
        print(f"SL     : {trade['stop_loss']}")
        print(f"TP     : {trade['take_profit']}")
        print(f"Volume : {trade['lot_size']}")


        return request



    def execute(self, request, signal=None, trade=None):


        if DRY_RUN:

            print("\n========== DRY RUN ==========\n")

            return None



        result = mt5.order_send(request)



        if result is None:

            raise Exception(
                "MT5 returned no result"
            )



        print("\n========== MT5 RESPONSE ==========\n")

        print(f"Retcode : {result.retcode}")
        print(f"Order   : {result.order}")
        print(f"Deal    : {result.deal}")
        print(f"Comment : {result.comment}")



        # ==============================
        # FAILED ORDER
        # ==============================

        if result.retcode != mt5.TRADE_RETCODE_DONE:


            print("\n========== TRADE FAILED ==========\n")

            print(
                f"Reason : {result.comment}"
            )


            return result



        # ==============================
        # SUCCESSFUL ORDER
        # ==============================


        if (
            signal is not None
            and trade is not None
        ):


            self.db.save_trade(

                ticket=result.order,

                symbol=SYMBOL,

                signal=signal["signal"],

                volume=trade["lot_size"],

                entry=request["price"],

                stop_loss=trade["stop_loss"],

                take_profit=trade["take_profit"],

                confidence=signal["confidence"],

                status="OPEN",

                open_time=str(datetime.now()),

            )


            print("\n========== DATABASE ==========\n")

            print(
                "Trade saved successfully."
            )



        print("\n========== MT5 SUCCESS ==========\n")

        print(
            f"Order : {result.order}"
        )

        print(
            f"Deal  : {result.deal}"
        )


        return result