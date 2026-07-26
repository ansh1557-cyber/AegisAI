"""
Aegis AI
Module: Trade Executor
Version: 0.2.0
"""

import MetaTrader5 as mt5

from engine.config import SYMBOL, DRY_RUN

class TradeExecutor:

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

            "magic": 20260726,

            "comment": "Aegis AI",

            "type_time": mt5.ORDER_TIME_GTC,

            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        if DRY_RUN:

            print("\n========== DRY RUN ==========\n")

            for key, value in request.items():
                print(f"{key}: {value}")

            return request

        return request