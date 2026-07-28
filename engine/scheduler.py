"""
Aegis AI
Module: Scheduler
Version: 2.1.0
"""

import threading
import time

from engine.logger import logger
from engine.trading_engine import TradingEngine
from engine.trade_monitor import TradeMonitor


class Scheduler:

    def __init__(self):

        self.engine = TradingEngine()
        self.monitor = TradeMonitor()

    def trading_loop(self):

        logger.info("Trading scheduler started.")

        while True:

            logger.info("Starting trading cycle.")

            self.engine.run()

            logger.info("Trading cycle completed.")

            logger.info("Waiting 60 seconds before next cycle.")

            time.sleep(60)

    def monitor_loop(self):

        logger.info("Trade monitor started.")

        self.monitor.monitor()

    def run(self):

        logger.info("Launching Scheduler.")

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