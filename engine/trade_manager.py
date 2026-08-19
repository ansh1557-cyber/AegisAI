"""
Aegis AI
Module: Trade Manager
Version: 0.4.1
"""

import MetaTrader5 as mt5

from engine.config import (
    BREAK_EVEN_R,
    PARTIAL_CLOSE_R,
    PARTIAL_CLOSE_PERCENT,
)


class TradeManager:

    def __init__(self):
        self.trade_states = {}

    # =====================================================
    # BREAK EVEN
    # =====================================================

    def move_to_break_even(self, position):
        
        if position.ticket not in self.trade_states:
            
            initial_risk = abs(position.price_open - position.sl)
            
            self.trade_states[position.ticket] = {
                "break_even": False,
                "partial_closed": False,
                "initial_risk": initial_risk,
            }

        state = self.trade_states[position.ticket]

        if state["break_even"]:
            return

        entry = position.price_open
        sl = position.sl
        tp = position.tp

        tick = mt5.symbol_info_tick(position.symbol)

        if tick is None:
            print("Unable to get market price.")
            return

        current = (
            tick.bid
            if position.type == mt5.ORDER_TYPE_BUY
            else tick.ask
        )

        risk = state["initial_risk"]

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

        # BUY
        if position.type == mt5.ORDER_TYPE_BUY:

            trigger = entry + (risk * BREAK_EVEN_R)

            print(f"Break-even Trigger : {trigger}")

            if current >= trigger and sl < entry:

                print("Moving BUY SL to Break Even...")

                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": position.ticket,
                    "symbol": position.symbol,
                    "sl": entry,
                    "tp": tp,
                }

                result = mt5.order_send(request)

                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    state["break_even"] = True
                    print("BUY moved to Break Even.")
                else:
                    print("Failed to move BUY SL.")

        # SELL
        else:

            trigger = entry - (risk * BREAK_EVEN_R)

            print(f"Break-even Trigger : {trigger}")

            if current <= trigger and sl > entry:

                print("Moving SELL SL to Break Even...")

                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "position": position.ticket,
                    "symbol": position.symbol,
                    "sl": entry,
                    "tp": tp,
                }

                result = mt5.order_send(request)

                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    state["break_even"] = True
                    print("SELL moved to Break Even.")
                else:
                    print("Failed to move SELL SL.")

    # =====================================================
    # TRAILING STOP
    # =====================================================

   

    def trail_stop(self, position):

        state = self.trade_states.get(position.ticket)

        if state is None:
            return

        if not state["break_even"]:
            return

        entry = position.price_open
        sl = position.sl
        tp = position.tp

        tick = mt5.symbol_info_tick(position.symbol)

        if tick is None:
            return

        current = (
            tick.bid
            if position.type == mt5.ORDER_TYPE_BUY
            else tick.ask
        )

        risk = state["initial_risk"]

        # BUY
        if position.type == mt5.ORDER_TYPE_BUY:

            trigger = entry + (risk * 2)

            if current >= trigger:

                new_sl = current - risk

                if new_sl > sl:

                    print(f"Trailing BUY -> {new_sl}")

                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": position.ticket,
                        "symbol": position.symbol,
                        "sl": round(new_sl, 2),
                        "tp": tp,
                    }

                    result = mt5.order_send(request)

                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print("BUY Trailing Updated")

        # SELL
        else:

            trigger = entry - (risk * 2)

            if current <= trigger:

                new_sl = current + risk

                if new_sl < sl:

                    print(f"Trailing SELL -> {new_sl}")

                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": position.ticket,
                        "symbol": position.symbol,
                        "sl": round(new_sl, 2),
                        "tp": tp,
                    }

                    result = mt5.order_send(request)

                    if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                        print("SELL Trailing Updated")
                    
    def partial_close(self, position):

        state = self.trade_states.get(position.ticket)

        if state is None:
            return

        if state["partial_closed"]:
            return

        entry = position.price_open
        sl = position.sl
        tp = position.tp

        tick = mt5.symbol_info_tick(position.symbol)

        if tick is None:
            return

        current = (
            tick.bid
            if position.type == mt5.ORDER_TYPE_BUY
            else tick.ask
        )

        risk = state["initial_risk"]

        if risk <= 0:
            return

        if position.type == mt5.ORDER_TYPE_BUY:
            trigger = entry + (risk * PARTIAL_CLOSE_R)
            
            if current >= trigger:

                close_volume = round(position.volume * PARTIAL_CLOSE_PERCENT, 2)

                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": position.ticket,
                    "symbol": position.symbol,
                    "volume": close_volume,
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": tick.bid,
                    "deviation": 20,
                    "magic": position.magic,
                    "comment": "Partial Close",
                }

                result = mt5.order_send(request)

                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    state["partial_closed"] = True
                print(f"✅ Partial Close Executed ({close_volume} lots)")

        else:

            trigger = entry - (risk * PARTIAL_CLOSE_R)

            if current <= trigger:

                close_volume = round(position.volume * PARTIAL_CLOSE_PERCENT, 2)

                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "position": position.ticket,
                    "symbol": position.symbol,
                    "volume": close_volume,
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": tick.ask,
                    "deviation": 20,
                    "magic": position.magic,
                    "comment": "Partial Close",
                }

                result = mt5.order_send(request)

                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    state["partial_closed"] = True
                    print(f"✅ Partial Close Executed ({close_volume} lots)")

            