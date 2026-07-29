"""
Test Account Information
"""

import MetaTrader5 as mt5

from engine.mt5_connector import MT5Connector


MT5Connector().connect()


account = mt5.account_info()


print("\n========== ACCOUNT INFO ==========\n")


print(f"Balance       : {account.balance}")
print(f"Equity        : {account.equity}")
print(f"Margin        : {account.margin}")
print(f"Free Margin   : {account.margin_free}")
print(f"Leverage      : {account.leverage}")


mt5.shutdown()