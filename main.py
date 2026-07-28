"""
Aegis AI
Main Application
Version: 1.0.0
"""

from engine.trade_monitor import TradeMonitor
from engine.scheduler import Scheduler


def main():

    print("=" * 50)
    print("🤖 AEGIS AI")
    print("Autonomous Trading System")
    print("=" * 50)
    
    scheduler = Scheduler()

    scheduler.run()
    
if __name__ == "__main__":
    main()