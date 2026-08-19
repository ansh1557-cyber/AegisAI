"""
Aegis AI
Module: Trade Monitor
Version: 0.4.2
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
        self.known_trades = set()

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
            print("Unable to retrieve MT5 deal history.")
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
        print(f"Ticket      : {deal.ticket}")
        print(f"Position ID : {deal.position_id}")
        print(f"Profit      : {deal.profit}")
        print(f"Price       : {deal.price}")
        print(f"Reason      : {deal.reason}")
        print()

        return deal

    # =====================================================
    # MONITOR
    # =====================================================

    def monitor(self):

        print(
            "Monitoring trades... "
            "Press Ctrl+C to stop.\n"
        )

        initial_positions = self.get_open_positions()

        previous_tickets = {
            position.ticket
            for position in initial_positions
        }

        self.known_trades.update(previous_tickets)

        try:

            while True:

                positions = self.get_open_positions()

                current_tickets = {
                    position.ticket
                    for position in positions
                }

                # -----------------------------
                # New Trades
                # -----------------------------

                new_tickets = (
                    current_tickets - previous_tickets
                )

                for position in positions:

                    # Trade management pipeline
                    self.trade_manager.move_to_break_even(
                        position
                    )

                    self.trade_manager.partial_close(
                        position
                    )

                    self.trade_manager.trail_stop(
                        position
                    )

                    # Announce genuinely new trades once
                    if position.ticket in new_tickets:

                        if position.ticket not in self.known_trades:

                            self.known_trades.add(
                                position.ticket
                            )

                            print(
                                "\n========== NEW TRADE =========="
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

                            TelegramNotifier().send_trade_opened(
                                position
                            )

                # -----------------------------
                # Closed Trades
                # -----------------------------

                closed_tickets = (
                    previous_tickets - current_tickets
                )

                for ticket in closed_tickets:

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

                    self.known_trades.discard(ticket)
                    self.trade_manager.remove_state(ticket)

                previous_tickets = current_tickets

                time.sleep(5)

        except KeyboardInterrupt:

            print("\nTrade monitor stopped.")