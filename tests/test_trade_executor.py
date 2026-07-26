"""
Test Trade Executor
"""

from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.bias import BiasEngine
from engine.entry import EntryEngine
from engine.risk_manager import RiskManager
from engine.trade_validator import TradeValidator
from engine.trade_executor import TradeExecutor


import MetaTrader5 as mt5

# Analyse market
analysis = MultiTimeframeAnalyzer().analyze()

# Get current price
entry_price = analysis["M15"]["data"]["Close"].iloc[-1]

# Market bias
bias = BiasEngine().analyze(analysis)

results = {
    "analysis": analysis,
    "bias": bias,
}

# Entry signal
signal = EntryEngine().analyze(results)

# Risk management
trade = RiskManager().calculate(
    analysis=analysis,
    signal=signal,
    entry_price=entry_price,
)

# Validation
validation = TradeValidator().validate(
    analysis,
    signal,
)

# Build order only if approved
if validation["approved"]:

    order = TradeExecutor().build_order(
        signal,
        trade,
    )

    print("\n========== ORDER ==========\n")

    for key, value in order.items():
        print(f"{key}: {value}")

else:

    print("\nTrade was rejected. No order created.")

mt5.shutdown()