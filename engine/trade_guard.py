"""
Aegis AI
Module: Trade Guard
Version: 0.2.0
"""

from datetime import datetime, timedelta

from engine.database import Database
import MetaTrader5 as mt5


class TradeGuard:


    def __init__(self):

        self.db = Database()

        # protection settings
        self.max_open_trades = 1
        self.cooldown_minutes = 15



    def can_trade(self, signal):


        trades = self.db.get_trades()
        
        positions = mt5.positions_get(symbol="XAUUSD")

        print("\n========== MT5 OPEN POSITIONS ==========")

        if positions:
            for p in positions:
                print(
                    f"Ticket={p.ticket} Magic={p.magic} Type={p.type}"
                )
        else:
            print("No open positions.")
        
        
            print("\n========== DATABASE ==========")
            print("Total trades:", len(trades))
        
        for trade in trades:
            print(trade)


        # ==========================
        # CHECK OPEN TRADES
        # ==========================

        open_trade_count = self.db.count_open_trades()

        if open_trade_count >= self.max_open_trades:

            print("\n========== TRADE GUARD ==========\n")
            print("⚠ Maximum open trades reached.")
            print("Skipping new trade.")

            return False



        # ==========================
        # CHECK LAST TRADE COOLDOWN
        # ==========================

        if len(trades) > 0:


            last_trade = trades[0]


            open_time = last_trade[11]


            # Handle datetime or string
            if isinstance(open_time, str):

                open_time = datetime.fromisoformat(open_time)


            now = datetime.now()


            difference = now - open_time



            if difference < timedelta(minutes=self.cooldown_minutes):


                print("\n========== TRADE GUARD ==========\n")
                print(
                    f"⚠ Cooldown active. "
                    f"Wait {self.cooldown_minutes} minutes."
                )

                return False



        return True