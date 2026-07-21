"""
Aegis AI
Module: MT5 Connector
Version: 0.3.0
"""

import MetaTrader5 as mt5
import pandas as pd


class MT5Connector:

    def connect(self):
        if not mt5.initialize():
            raise Exception(f"MT5 Initialization Failed: {mt5.last_error()}")

        print("Connected to MetaTrader 5")
        return True

    def disconnect(self):
        mt5.shutdown()

    def get_rates(
        self,
        symbol="XAUUSD",
        timeframe=mt5.TIMEFRAME_M15,
        bars=500,
    ):

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)

        if rates is None:
            raise Exception("Failed to download market data.")

        df = pd.DataFrame(rates)

        df.rename(
            columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
            },
            inplace=True,
        )

        return df