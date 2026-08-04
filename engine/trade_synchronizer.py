"""
Aegis AI
Module: Trade Synchronizer
Version: 1.0.0
"""

from datetime import datetime
import MetaTrader5 as mt5

from engine.database import Database
from engine.config import SYMBOL, MAGIC_NUMBER


class TradeSynchronizer:

    def __init__(self):

        self.db = Database()

    def sync(self):

        print("\n========== TRADE SYNCHRONIZER ==========\n")
        
        if not mt5.initialize():
            print("Unable to initialize MT5")
            print(mt5.last_error())
            return

        positions = mt5.positions_get(symbol=SYMBOL)

        if positions is None:
            print("Unable to read MT5 positions.")
            return

        mt5_tickets = set()

        for position in positions:

            if position.magic == MAGIC_NUMBER:
                mt5_tickets.add(position.ticket)

        trades = self.db.get_trades()

        fixed = 0

        for trade in trades:

            ticket = trade[1]
            status = trade[9]

            if status != "OPEN":
                continue

            if ticket not in mt5_tickets:

                print(f"Closing stale database trade {ticket}")

                self.db.update_trade(
                    ticket=ticket,
                    status="CLOSED",
                    profit=0,
                    close_time=str(datetime.now())
                )

                fixed += 1

        print(f"Synchronized {fixed} trade(s).")