"""
Aegis AI
Module: Trade Executor
Version: 0.2.1
"""

import MetaTrader5 as mt5

from engine.config import SYMBOL, DRY_RUN, MAGIC_NUMBER



class TradeExecutor:
    
    def has_open_trade(self, signal):

        import MetaTrader5 as mt5

        from engine.config import SYMBOL, MAGIC_NUMBER

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

        # Get current market price
        tick = mt5.symbol_info_tick(SYMBOL)

        if tick is None:
            raise Exception(f"Unable to get price for {SYMBOL}")

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
            "deviation": 10,
            "magic": MAGIC_NUMBER,
            "comment": "Aegis AI",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        if DRY_RUN:

            print("\n========== DRY RUN ==========\n")

            for key, value in request.items():
                print(f"{key}: {value}")

        return request

    def execute(self, request):

        result = mt5.order_send(request)

        if result is None:
            raise Exception("MT5 returned no result.")

        print("\n========== MT5 RESPONSE ==========\n")
        print(f"Retcode : {result.retcode}")
        print(f"Order    : {result.order}")
        print(f"Deal     : {result.deal}")
        print(f"Comment  : {result.comment}")

        return result