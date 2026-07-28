"""
Aegis AI
Module: Scheduler
Version: 1.0.0
"""

import time

from engine.trading_engine import TradingEngine


class Scheduler:

    def __init__(self):

        self.engine = TradingEngine()

    def run(self):

        print("\n========== SCHEDULER ==========\n")

        while True:

            print("Starting trading cycle...\n")

            self.engine.run()

            print("\nTrading cycle finished.")
            print("Waiting 60 seconds...\n")

            time.sleep(60)