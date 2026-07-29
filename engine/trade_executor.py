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



        symbol_info = mt5.symbol_info(SYMBOL)


        if symbol_info is None:

            raise Exception(
                f"Unable to get symbol information for {SYMBOL}"
            )



        tick = mt5.symbol_info_tick(SYMBOL)


        if tick is None:

            raise Exception(
                f"Unable to get price for {SYMBOL}"
            )



        # -----------------------------
        # Direction
        # -----------------------------

        if signal["signal"] == "BUY":

            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask


        else:

            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid



        sl = trade["stop_loss"]
        tp = trade["take_profit"]



        # -----------------------------
        # Broker minimum stop distance
        # -----------------------------

        minimum_distance = (
            symbol_info.trade_stops_level
            *
            symbol_info.point
        )


        # Some brokers return 0
        # XAUUSD safety buffer

        if minimum_distance == 0:

            minimum_distance = 0.50



        # -----------------------------
        # BUY validation
        # -----------------------------

        if signal["signal"] == "BUY":


            if sl >= price:

                sl = price - minimum_distance



            if tp <= price:

                tp = price + minimum_distance



        # -----------------------------
        # SELL validation
        # -----------------------------

        else:


            if sl <= price:

                sl = price + minimum_distance



            if tp >= price:

                tp = price - minimum_distance




        request = {


            "action":
                mt5.TRADE_ACTION_DEAL,


            "symbol":
                SYMBOL,


            "volume":
                trade["lot_size"],


            "type":
                order_type,


            "price":
                price,


            "sl":
                round(sl,2),


            "tp":
                round(tp,2),


            "deviation":
                10,


            "magic":
                MAGIC_NUMBER,


            "comment":
                "Aegis AI",


            "type_time":
                mt5.ORDER_TIME_GTC,


            "type_filling":
                mt5.ORDER_FILLING_IOC,

        }



        print("\n========== ORDER DEBUG ==========\n")

        print(f"Symbol : {SYMBOL}")
        print(f"Type   : {signal['signal']}")
        print(f"Entry  : {price}")
        print(f"SL     : {request['sl']}")
        print(f"TP     : {request['tp']}")
        print(f"Volume : {request['volume']}")



        if DRY_RUN:


            print("\n========== DRY RUN ==========\n")


            for key,value in request.items():

                print(
                    f"{key}: {value}"
                )



        return request





    def execute(self, request, signal=None, trade=None):


        result = mt5.order_send(request)



        if result is None:

            raise Exception(
                "MT5 returned no result."
            )



        print("\n========== MT5 RESPONSE ==========\n")

        print(
            f"Retcode : {result.retcode}"
        )

        print(
            f"Order   : {result.order}"
        )

        print(
            f"Deal    : {result.deal}"
        )

        print(
            f"Comment : {result.comment}"
        )



        # -----------------------------
        # Failed order
        # -----------------------------

        if result.retcode != mt5.TRADE_RETCODE_DONE:


            print("\n========== TRADE FAILED ==========\n")

            print(
                f"Reason : {result.comment}"
            )


            return result




        # -----------------------------
        # Save successful trade
        # -----------------------------

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

                stop_loss=request["sl"],

                take_profit=request["tp"],

                confidence=signal["confidence"],

                status="OPEN",

                open_time=str(datetime.now()),

            )



            print("\n========== DATABASE ==========\n")

            print(
                "Trade saved successfully."
            )



        return result