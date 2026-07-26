"""
Aegis AI
Module: Multi-Timeframe Analyzer
Version: 0.5.0
"""

from engine.mt5_connector import MT5Connector
from engine.analyzer import MarketAnalyzer
from engine.timeframes import TIMEFRAMES
from engine.config import SYMBOL, BARS


class MultiTimeframeAnalyzer:

    def __init__(self):

        self.connector = MT5Connector()
        self.analyzer = MarketAnalyzer()

    def analyze(self):

        self.connector.connect()

        results = {}

        for name, timeframe in TIMEFRAMES.items():

            print(f"\nAnalyzing {name}...")

            df = self.connector.get_rates(
                symbol=SYMBOL,
                timeframe=timeframe,
                bars=BARS
            )

            results[name] = self.analyzer.analyze(df)

       

        return results