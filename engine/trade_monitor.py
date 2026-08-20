"""
Aegis AI
Module: Trade Monitor
Version: 0.4.5
"""

import time
from datetime import datetime, timedelta

import MetaTrader5 as mt5

from engine.telegram import TelegramNotifier
from engine.config import SYMBOL, MAGIC_NUMBER
from engine.database import Database
from engine.trade_manager import TradeManager


class TradeMonitor:

    def __init__(self):

        self.db = Database()
        self.trade_manager = TradeManager()

        # Tickets known by the monitor.
        self.known_trades = set()

        # First successful MT5 snapshot.
        self.startup_synchronized = False

    # =====================================================
    # OPEN POSITIONS
    # =====================================================

    def get_open_positions(self):

        positions = mt5.positions_get(symbol=SYMBOL)

        if positions is None:
            return []

        return [
            position
            for position in positions
            if position.magic == MAGIC_NUMBER
        ]

    # =====================================================
    # DATABASE TRADE CHECK
    # =====================================================

    def is_existing_database_trade(self, ticket):
        """
        Check whether this ticket already exists in the database
        as an OPEN trade.

        Database schema:
        trade[1] = ticket
        trade[9] = status
        """

        try:

            trades = self.db.get_trades()

            for trade in trades:

                if trade[1] == ticket:

                    return trade[9] == "OPEN"

        except Exception as exc:

            print(
                f"Database trade lookup failed: {exc}"
            )

        return False

    # =====================================================
    # DEAL LOOKUP
    # =====================================================

    def get_deal(self, position_id):

        date_to = datetime.now()
        date_from = date_to - timedelta(days=30)

        deals = mt5.history_deals_get(
            date_from,
            date_to
        )

        if deals is None:

            print(
                "Unable to retrieve MT5 deal history."
            )

            return None

        position_deals = [
            deal
            for deal in deals
            if deal.position_id == position_id
        ]

        if not position_deals:

            print(
                f"No deal found for position {position_id}"
            )

            return None

        position_deals.sort(
            key=lambda deal: deal.time
        )

        deal = position_deals[-1]

        print("\n========== LAST DEAL ==========")
        print(
            f"Ticket      : {deal.ticket}"
        )
        print(
            f"Position ID : {deal.position_id}"
        )
        print(
            f"Profit      : {deal.profit}"
        )
        print(
            f"Price       : {deal.price}"
        )
        print(
            f"Reason      : {deal.reason}"
        )
        print()

        return deal

    # =====================================================
    # PRINT POSITION
    # =====================================================

    def print_position(self, position, title):

        print(
            f"\n========== {title} =========="
        )

        print(
            f"Ticket : {position.ticket}"
        )

        print(
            f"Symbol : {position.symbol}"
        )

        print(
            "Type   : "
            f"{'BUY' if position.type == mt5.ORDER_TYPE_BUY else 'SELL'}"
        )

        print(
            f"Volume : {position.volume}"
        )

        print(
            f"Open   : {position.price_open}"
        )

        print(
            f"SL     : {position.sl}"
        )

        print(
            f"TP     : {position.tp}"
        )

    # =====================================================
    # EXISTING TRADE RECOVERY
    # =====================================================

    def recover_existing_position(self, position):

        # Build/recover TradeManager state.
        self.trade_manager._get_state(
            position
        )

        self.known_trades.add(
            position.ticket
        )

        self.print_position(
            position,
            "EXISTING TRADE RECOVERED"
        )

    # =====================================================
    # NEW TRADE
    # =====================================================

    def handle_new_trade(self, position):

        self.known_trades.add(
            position.ticket
        )

        self.print_position(
            position,
            "NEW TRADE"
        )

        TelegramNotifier().send_trade_opened(
            position
        )

    # =====================================================
    # CLOSED TRADE
    # =====================================================

    def handle_closed_trade(self, ticket):

        deal = self.get_deal(ticket)

        print(
            "\n========== TRADE CLOSED =========="
        )

        print(
            f"Ticket : {ticket}"
        )

        if deal:

            print(
                f"Profit : {deal.profit}"
            )

            print(
                f"Price  : {deal.price}"
            )

            self.db.update_trade(
                ticket=ticket,
                status="CLOSED",
                profit=deal.profit,
                close_time=str(
                    datetime.now()
                ),
            )

            print(
                "Database updated successfully."
            )

        TelegramNotifier().send_trade_closed(
            ticket,
            deal
        )

        self.known_trades.discard(
            ticket
        )

        self.trade_manager.remove_state(
            ticket
        )

    # =====================================================
    # MONITOR
    # =====================================================

    def monitor(self):

        print(
            "Monitoring trades... "
            "Press Ctrl+C to stop.\n"
        )

        # Important:
        # The scheduler starts TradeMonitor and TradingEngine
        # concurrently. Therefore the first snapshot can be
        # empty even when TradingEngine is about to expose a
        # position.
        previous_tickets = set()

        try:

            while True:

                positions = self.get_open_positions()

                current_tickets = {
                    position.ticket
                    for position in positions
                }

                # =================================================
                # STARTUP SYNCHRONIZATION
                # =================================================

                if not self.startup_synchronized:

                    for position in positions:

                        self.recover_existing_position(
                            position
                        )

                    previous_tickets = (
                        current_tickets.copy()
                    )

                    self.startup_synchronized = True

                else:

                    # =================================================
                    # TRADE MANAGEMENT
                    # =================================================

                    for position in positions:

                        self.trade_manager.move_to_break_even(
                            position
                        )

                        self.trade_manager.partial_close(
                            position
                        )

                        self.trade_manager.trail_stop(
                            position
                        )

                    # =================================================
                    # NEW TICKETS
                    # =================================================

                    new_tickets = (
                        current_tickets
                        - previous_tickets
                    )

                    for ticket in new_tickets:

                        position = next(
                            (
                                p
                                for p in positions
                                if p.ticket == ticket
                            ),
                            None
                        )

                        if position is None:
                            continue

                        # -------------------------------------------------
                        # If the trading engine saved this trade to the DB
                        # already, it is an existing trade from the monitor's
                        # point of view, not a new notification.
                        # -------------------------------------------------

                        if self.is_existing_database_trade(
                            ticket
                        ):

                            self.recover_existing_position(
                                position
                            )

                        else:

                            # Make sure TradeManager state exists.
                            self.trade_manager._get_state(
                                position
                            )

                            self.handle_new_trade(
                                position
                            )

                    # =================================================
                    # CLOSED TICKETS
                    # =================================================

                    closed_tickets = (
                        previous_tickets
                        - current_tickets
                    )

                    for ticket in closed_tickets:

                        self.handle_closed_trade(
                            ticket
                        )

                previous_tickets = (
                    current_tickets.copy()
                )

                time.sleep(5)

        except KeyboardInterrupt:

            print(
                "\nTrade monitor stopped."
            )