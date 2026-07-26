"""
Test Trade Executor
"""

from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.bias import BiasEngine
from engine.entry import EntryEngine
from engine.risk_manager import RiskManager
from engine.trade_validator import TradeValidator
from engine.trade_executor import TradeExecutor
from engine.config import DRY_RUN


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

    executor = TradeExecutor()

    request = executor.build_order(
        signal,
        trade,
    )

    if DRY_RUN:

        print("\n========== DRY RUN COMPLETED ==========\n")

    else:

        result = executor.execute(request)

        print("\n========== MT5 RESULT ==========\n")

        print(f"Retcode : {result.retcode}")
        print(f"Order   : {result.order}")
        print(f"Deal    : {result.deal}")
        print(f"Comment : {result.comment}")

else:

    print("\nTrade was rejected. No order created.")

mt5.shutdown()