"""
Aegis AI
Module: Trade Monitor
Version: 0.4.0
"""

import time
import MetaTrader5 as mt5
from datetime import datetime

from engine.telegram import TelegramNotifier
from engine.config import SYMBOL, MAGIC_NUMBER
from engine.database import Database


class TradeMonitor:

    def __init__(self):
        self.db = Database()

    def get_open_positions(self):

        positions = mt5.positions_get(symbol=SYMBOL)

        if positions is None:
            return []

        positions = [
            position
            for position in positions
            if position.magic == MAGIC_NUMBER
        ]

        return positions

    def get_deal(self, position_id):

        deals = mt5.history_deals_get(position=position_id)

        if deals is None or len(deals) == 0:
            return None

        return deals[-1]

        print("\n========== LAST DEAL ==========\n")
        print(f"Ticket      : {deal.ticket}")
        print(f"Position ID : {deal.position_id}")
        print(f"Profit      : {deal.profit}")
        print(f"Price       : {deal.price}")
        print(f"Reason      : {deal.reason}")
        print()

        return deal

    def monitor(self):

        print("Monitoring trades... Press Ctrl+C to stop.\n")

        previous_tickets = {
            position.ticket
            for position in self.get_open_positions()
        }
        trade_history = {}

        try:

            while True:

                positions = self.get_open_positions()

                current_tickets = {position.ticket for position in positions}

                # -----------------------------
                # New Trades
                # -----------------------------
                new_tickets = current_tickets - previous_tickets

                for position in positions:

                    if position.ticket in new_tickets:

                        print("\n========== NEW TRADE ==========\n")
                        print(f"Ticket : {position.ticket}")
                        print(f"Symbol : {position.symbol}")
                        print(f"Type   : {'BUY' if position.type == mt5.ORDER_TYPE_BUY else 'SELL'}")
                        print(f"Volume : {position.volume}")
                        print(f"Open   : {position.price_open}")
                        print(f"SL     : {position.sl}")
                        print(f"TP     : {position.tp}")

                        trade_history[position.ticket] = {
                            "entry": position.price_open,
                            "type": position.type,
                            "volume": position.volume,
                            "time": position.time,
                        }

                        TelegramNotifier().send_trade_opened(position)

                # -----------------------------
                # Closed Trades
                # -----------------------------
                closed_tickets = previous_tickets - current_tickets

                for ticket in closed_tickets:

                    deal = self.get_deal(ticket)

                    print("\n========== TRADE CLOSED ==========\n")
                    print(f"Ticket : {ticket}")

                    if deal:

                        print(f"Profit : {deal.profit}")
                        print(f"Price  : {deal.price}")
                        
                        self.db.close_trade(
                            ticket=ticket,
                            profit=deal.profit,
                            close_time=str(datetime.now()),
                        )

                        print("Database updated successfully.")

                    TelegramNotifier().send_trade_closed(ticket, deal)

                previous_tickets = current_tickets

                time.sleep(5)

        except KeyboardInterrupt:

            print("\nTrade monitor stopped.")