"""
Aegis AI
Module: Trade Monitor
Version: 0.3.0
"""

import time
import MetaTrader5 as mt5

from engine.config import SYMBOL, MAGIC_NUMBER


class TradeMonitor:

    def get_open_positions(self):

        positions = mt5.positions_get(symbol=SYMBOL)

        if positions is None:
            return []

        # Only keep Aegis AI trades
        positions = [
            position
            for position in positions
            if position.magic == MAGIC_NUMBER
        ]

        return positions

    def monitor(self):

        print("Monitoring trades... Press Ctrl+C to stop.\n")

        previous_tickets = set()

        try:

            while True:

                positions = self.get_open_positions()

                current_tickets = {position.ticket for position in positions}

                # New trades
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

                # Closed trades
                closed_tickets = previous_tickets - current_tickets

                for ticket in closed_tickets:

                    print("\n========== TRADE CLOSED ==========\n")
                    print(f"Ticket : {ticket}")

                previous_tickets = current_tickets

                time.sleep(5)

        except KeyboardInterrupt:

            print("\nTrade monitor stopped.")