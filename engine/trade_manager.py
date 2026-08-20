"""
Aegis AI
Module: Trade Manager
Version: 0.5.1
"""

import math
from datetime import datetime, timedelta

import MetaTrader5 as mt5

from engine.config import (
    BREAK_EVEN_R,
    TRAIL_AFTER_R,
    TRAIL_STEP_R,
    PARTIAL_CLOSE_R,
    PARTIAL_CLOSE_PERCENT,
    RISK_REWARD,
)


class TradeManager:

    def __init__(self):
        self.trade_states = {}

    # =====================================================
    # STATE
    # =====================================================

    def _has_partial_close(self, position):
        """Return True when MT5 history shows a partial exit."""

        date_to = datetime.now()
        date_from = date_to - timedelta(days=30)

        deals = mt5.history_deals_get(date_from, date_to)

        if deals is None:
            return False

        position_deals = [
            deal
            for deal in deals
            if deal.position_id == position.ticket
        ]

        if not position_deals:
            return False

        entry_volume = sum(
            float(deal.volume)
            for deal in position_deals
            if deal.entry == mt5.DEAL_ENTRY_IN
        )

        exit_volume = sum(
            float(deal.volume)
            for deal in position_deals
            if deal.entry == mt5.DEAL_ENTRY_OUT
        )

        if (
            entry_volume > 0
            and exit_volume > 0
            and exit_volume < entry_volume
            and float(position.volume) < entry_volume
        ):
            return True

        return False

    def _get_state(self, position):
        """Create or recover management state for a position."""

        ticket = position.ticket

        if ticket in self.trade_states:
            return self.trade_states[ticket]

        entry = float(position.price_open)
        sl = float(position.sl)
        tp = float(position.tp)
        current_volume = float(position.volume)

        # Recover original risk from the current SL.
        initial_risk = abs(entry - sl)

        # If SL is already at break-even, recover the original
        # risk from TP and the configured risk/reward.
        if initial_risk <= 0 and RISK_REWARD > 0:
            initial_risk = abs(tp - entry) / RISK_REWARD

        break_even = abs(sl - entry) < 1e-6
        partial_closed = self._has_partial_close(position)

        state = {
            "initial_risk": initial_risk,
            "break_even": break_even,
            "partial_closed": partial_closed,
            "partial_unavailable": False,
            "last_trail_level": None,
            "initial_volume": current_volume,
        }

        self.trade_states[ticket] = state

        print("\n========== TRADE STATE RECOVERED ==========")
        print(f"Ticket          : {ticket}")
        print(f"Initial Risk    : {initial_risk}")
        print(f"Break-Even      : {break_even}")
        print(f"Partial Closed  : {partial_closed}")
        print(f"Current Volume  : {current_volume}")

        return state

    def remove_state(self, ticket):
        self.trade_states.pop(ticket, None)

    # =====================================================
    # MARKET PRICE
    # =====================================================

    def _get_market(self, position):

        tick = mt5.symbol_info_tick(position.symbol)

        if tick is None:
            return None, None

        if position.type == mt5.ORDER_TYPE_BUY:
            return tick.bid, tick

        return tick.ask, tick

    # =====================================================
    # MODIFY SL
    # =====================================================

    def _modify_sl(self, position, new_sl):

        symbol_info = mt5.symbol_info(position.symbol)

        if symbol_info is None:
            print("❌ Unable to read symbol information.")
            return False

        new_sl = round(
            float(new_sl),
            symbol_info.digits
        )

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": position.ticket,
            "symbol": position.symbol,
            "sl": new_sl,
            "tp": position.tp,
        }

        result = mt5.order_send(request)

        if result is None:
            print("❌ MT5 returned no response.")
            return False

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(
                f"❌ SL update failed | "
                f"Retcode={result.retcode} | "
                f"Comment={result.comment}"
            )
            return False

        print(f"✅ SL updated -> {new_sl}")

        return True

    # =====================================================
    # BREAK EVEN
    # =====================================================

    def move_to_break_even(self, position):

        state = self._get_state(position)

        if state["break_even"]:
            return

        risk = float(state["initial_risk"])

        if risk <= 0:
            print(
                f"⚠ Ticket {position.ticket}: "
                "initial risk unavailable."
            )
            return

        entry = float(position.price_open)

        current, _ = self._get_market(position)

        if current is None:
            return

        if position.type == mt5.ORDER_TYPE_BUY:

            trigger = entry + (
                risk * BREAK_EVEN_R
            )

            if current < trigger:
                return

            if position.sl >= entry:
                state["break_even"] = True
                return

        else:

            trigger = entry - (
                risk * BREAK_EVEN_R
            )

            if current > trigger:
                return

            if position.sl <= entry:
                state["break_even"] = True
                return

        print("\n========== BREAK EVEN ==========")
        print(f"Ticket : {position.ticket}")
        print(f"Entry  : {entry}")
        print(f"Current: {current}")
        print(f"Trigger: {trigger}")

        if self._modify_sl(position, entry):
            state["break_even"] = True
            print("✅ Break-Even activated.")

    # =====================================================
    # PARTIAL CLOSE
    # =====================================================

    def partial_close(self, position):

        state = self._get_state(position)

        if state["partial_closed"]:
            return

        if state["partial_unavailable"]:
            return

        risk = float(state["initial_risk"])

        if risk <= 0:
            return

        entry = float(position.price_open)

        current, tick = self._get_market(position)

        if current is None or tick is None:
            return

        if position.type == mt5.ORDER_TYPE_BUY:

            trigger = entry + (
                risk * PARTIAL_CLOSE_R
            )

            if current < trigger:
                return

        else:

            trigger = entry - (
                risk * PARTIAL_CLOSE_R
            )

            if current > trigger:
                return

        symbol_info = mt5.symbol_info(position.symbol)

        if symbol_info is None:
            print("❌ Unable to read symbol volume rules.")
            return

        min_volume = float(symbol_info.volume_min)
        volume_step = float(symbol_info.volume_step)
        current_volume = float(position.volume)

        desired_close = (
            current_volume * PARTIAL_CLOSE_PERCENT
        )

        if volume_step <= 0:
            volume_step = min_volume

        close_volume = (
            math.floor(
                desired_close / volume_step
            ) * volume_step
        )

        close_volume = round(close_volume, 8)

        remaining_volume = round(
            current_volume - close_volume,
            8
        )

        print("\n========== PARTIAL CLOSE ==========")
        print(f"Ticket         : {position.ticket}")
        print(f"Current        : {current}")
        print(f"Trigger        : {trigger}")
        print(f"Current Volume : {current_volume}")
        print(f"Target Close   : {close_volume}")
        print(f"Min Volume     : {min_volume}")
        print(f"Volume Step    : {volume_step}")

        if close_volume < min_volume:
            print(
                "⚠ Partial close unavailable: "
                "position is too small for broker volume rules."
            )
            state["partial_unavailable"] = True
            return

        if close_volume >= current_volume:
            print(
                "⚠ Partial close cancelled: "
                "calculated close volume would close "
                "the entire position."
            )
            state["partial_unavailable"] = True
            return

        if (
            remaining_volume > 0
            and remaining_volume < min_volume
        ):
            print(
                "⚠ Partial close cancelled: "
                "remaining position would be below "
                "broker minimum."
            )
            state["partial_unavailable"] = True
            return

        if position.type == mt5.ORDER_TYPE_BUY:
            close_type = mt5.ORDER_TYPE_SELL
            close_price = tick.bid
        else:
            close_type = mt5.ORDER_TYPE_BUY
            close_price = tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": close_volume,
            "type": close_type,
            "price": close_price,
            "deviation": 20,
            "magic": position.magic,
            "comment": "Aegis Partial Close",
        }

        result = mt5.order_send(request)

        if result is None:
            print(
                "❌ Partial close failed: "
                "no MT5 response."
            )
            return

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(
                f"❌ Partial close failed | "
                f"Retcode={result.retcode} | "
                f"Comment={result.comment}"
            )
            return

        state["partial_closed"] = True

        print("✅ PARTIAL CLOSE EXECUTED")
        print(f"Closed   : {close_volume}")
        print(f"Remaining: {remaining_volume}")

    # =====================================================
    # TRAILING STOP
    # =====================================================

    def trail_stop(self, position):

        state = self._get_state(position)

        if not state["break_even"]:
            return

        risk = float(state["initial_risk"])

        if risk <= 0:
            return

        entry = float(position.price_open)

        current, _ = self._get_market(position)

        if current is None:
            return

        if position.type == mt5.ORDER_TYPE_BUY:
            profit_distance = current - entry
        else:
            profit_distance = entry - current

        current_r = profit_distance / risk

        if current_r < TRAIL_AFTER_R:
            return

        if TRAIL_STEP_R <= 0:
            return

        steps = math.floor(
            (
                current_r - TRAIL_AFTER_R
            ) / TRAIL_STEP_R
        )

        if steps < 0:
            return

        locked_r = (
            TRAIL_AFTER_R
            - TRAIL_STEP_R
            + (
                steps * TRAIL_STEP_R
            )
        )

        last_level = state["last_trail_level"]

        if (
            last_level is not None
            and locked_r <= last_level
        ):
            return

        if position.type == mt5.ORDER_TYPE_BUY:

            new_sl = (
                entry
                + (
                    risk * locked_r
                )
            )

            if new_sl <= position.sl:
                return

        else:

            new_sl = (
                entry
                - (
                    risk * locked_r
                )
            )

            if new_sl >= position.sl:
                return

        print("\n========== TRAILING STOP ==========")
        print(f"Ticket     : {position.ticket}")
        print(f"Current R  : {current_r:.2f}")
        print(f"Locking R  : {locked_r:.2f}")
        print(f"Current SL : {position.sl}")
        print(f"New SL     : {new_sl}")

        if self._modify_sl(position, new_sl):
            state["last_trail_level"] = locked_r
            print(
                f"✅ Trailing level "
                f"{locked_r:.2f}R activated."
            )