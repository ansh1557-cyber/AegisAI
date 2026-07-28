"""
Aegis AI
Module: Scheduler
Version: 2.0.0
"""

import threading
import time

from engine.trading_engine import TradingEngine
from engine.trade_monitor import TradeMonitor


class Scheduler:

    def __init__(self):

        self.engine = TradingEngine()
        self.monitor = TradeMonitor()

    def trading_loop(self):

        print("\n========== TRADING LOOP ==========\n")

        while True:

            print("Starting trading cycle...\n")

            self.engine.run()

            print("\nTrading cycle finished.")
            print("Waiting 60 seconds...\n")

            time.sleep(60)

    def monitor_loop(self):

        self.monitor.monitor()

    def run(self):

        trading_thread = threading.Thread(
            target=self.trading_loop,
            daemon=True,
        )

        monitor_thread = threading.Thread(
            target=self.monitor_loop,
            daemon=True,
        )

        trading_thread.start()
        monitor_thread.start()

        trading_thread.join()
        monitor_thread.join()