"""
Aegis AI
Module: Trade Manager
Version: 0.4.1
"""

import MetaTrader5 as mt5

from engine.config import BREAK_EVEN_R


class TradeManager:

    def __init__(self):
        pass

    def move_to_break_even(self, position):

        entry = position.price_open
        sl = position.sl
        tp = position.tp

        # Get current market tick
        tick = mt5.symbol_info_tick(position.symbol)

        if tick is None:
            print("Unable to get market price.")
            return

        # Current market price
        current = (
            tick.bid
            if position.type == mt5.ORDER_TYPE_BUY
            else tick.ask
        )

        risk = abs(entry - sl)

        print("\n========== TRADE MANAGER ==========")
        print(f"Ticket : {position.ticket}")
        print(f"Entry  : {entry}")
        print(f"Current: {current}")
        print(f"SL     : {sl}")
        print(f"TP     : {tp}")
        print(f"Risk   : {risk}")

        if risk <= 0:
            print("Invalid risk.")
            return

        # ==========================
        # BUY
        # ==========================
        if position.type == mt5.ORDER_TYPE_BUY:

            trigger = entry + (risk * BREAK_EVEN_R)

            print(f"Break-even Trigger : {trigger}")

            if current >= trigger:

                if sl < entry:

                    print("Moving BUY SL to Break Even...")

                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": position.ticket,
                        "symbol": position.symbol,
                        "sl": entry,
                        "tp": tp,
                    }

                    result = mt5.order_send(request)

                    if result is None:
                        print("MT5 request failed.")
                        return

                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print("BUY moved to Break Even successfully.")
                    else:
                        print(f"Failed: {result.comment}")

        # ==========================
        # SELL
        # ==========================
        else:

            trigger = entry - (risk * BREAK_EVEN_R)

            print(f"Break-even Trigger : {trigger}")

            if current <= trigger:

                if sl > entry:

                    print("Moving SELL SL to Break Even...")

                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": position.ticket,
                        "symbol": position.symbol,
                        "sl": entry,
                        "tp": tp,
                    }

                    result = mt5.order_send(request)

                    if result is None:
                        print("MT5 request failed.")
                        return

                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print("SELL moved to Break Even successfully.")
                    else:
                        print(f"Failed: {result.comment}")