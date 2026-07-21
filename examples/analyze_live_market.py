"""
Aegis AI
Example: Live Market Analysis
Version: 0.3.3
"""

print("RUNNING NEW ANALYZE_LIVE_MARKET")

from engine.mt5_connector import MT5Connector
from engine.analyzer import MarketAnalyzer

connector = MT5Connector()

if connector.connect():

    print("Connected to MetaTrader 5")

    print("Getting market data...")
    df = connector.get_rates(
        symbol="XAUUSD",
        bars=500
    )

    print("Data received:", df is not None)

    if df is not None:
        print("Rows:", len(df))

        print("Creating analyzer...")
        analyzer = MarketAnalyzer()

        print("Running analysis...")
        result = analyzer.analyze(df)

        print("Analysis finished!")

        print("\n========== AEGIS AI REPORT ==========")

        print("Trend:", result["structure"]["trend"])
        print("Swing Highs:", len(result["swings"]["swing_highs"]))
        print("Swing Lows:", len(result["swings"]["swing_lows"]))

        print("Bullish BOS:", result["bos"]["bullish_bos"])
        print("Bearish BOS:", result["bos"]["bearish_bos"])

        print("Bullish CHoCH:", result["choch"]["bullish_choch"])
        print("Bearish CHoCH:", result["choch"]["bearish_choch"])

        print("Bullish FVGs:", len(result["fvg"]["bullish_fvg"]))
        print("Bearish FVGs:", len(result["fvg"]["bearish_fvg"]))

        print("Buy-side Sweeps:", len(result["liquidity"]["buy_side_sweeps"]))
        print("Sell-side Sweeps:", len(result["liquidity"]["sell_side_sweeps"]))

        print("====================================")

    connector.disconnect()