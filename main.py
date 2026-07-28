"""
Aegis AI
Main Application
Version: 1.0.0
"""

from engine.trade_monitor import TradeMonitor
from engine.trading_engine import TradingEngine


def main():

    print("=" * 50)
    print("🤖 AEGIS AI")
    print("Autonomous Trading System")
    print("=" * 50)
    
    engine = TradingEngine()

    engine.run()
    monitor = TradeMonitor()
    monitor.monitor()


if __name__ == "__main__":
    main()