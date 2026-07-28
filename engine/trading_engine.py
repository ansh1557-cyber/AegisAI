"""
Aegis AI
Module: Trading Engine
Version: 1.2.0
"""

from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.bias import BiasEngine
from engine.entry import EntryEngine
from engine.risk_manager import RiskManager
from engine.trade_validator import TradeValidator
from engine.trade_executor import TradeExecutor
from engine.telegram import TelegramNotifier
from engine.config import DRY_RUN


class TradingEngine:

    def analyze_market(self):

        analysis = MultiTimeframeAnalyzer().analyze()

        entry_price = analysis["M15"]["data"]["Close"].iloc[-1]

        return analysis, entry_price

    def generate_signal(self, analysis):

        bias = BiasEngine().analyze(analysis)

        results = {
            "analysis": analysis,
            "bias": bias,
        }

        signal = EntryEngine().analyze(results)

        return signal

    def calculate_trade(self, analysis, signal, entry_price):

        trade = RiskManager().calculate(
            analysis=analysis,
            signal=signal,
            entry_price=entry_price,
        )

        return trade

    def validate_trade(self, analysis, signal):

        validation = TradeValidator().validate(
            analysis,
            signal,
        )

        return validation
    
    def execute_trade(self, signal, trade, validation):

        if validation["approved"]:

           executor = TradeExecutor()

           request = executor.build_order(
               signal,
               trade,
            )

           TelegramNotifier().send_trade(
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

            TelegramNotifier().send_rejection(
                signal,
                validation["checks"],
           )

            print("\nTrade was rejected. No order created.")

    def run(self):

        print("\n========== TRADING ENGINE ==========\n")

        analysis, entry_price = self.analyze_market()

        signal = self.generate_signal(analysis)

        trade = self.calculate_trade(
            analysis,
            signal,
            entry_price,
        )

        validation = self.validate_trade(
            analysis,
            signal,
        )

        print("\n========== TRADE VALIDATION ==========\n")

        if validation["approved"]:
            print("✅ TRADE APPROVED")
        else:
            print("❌ TRADE REJECTED")

        for check in validation["checks"]:
            print(check)
            
        self.execute_trade(
            signal,
            trade,
            validation,
        )

        return {
            "analysis": analysis,
            "signal": signal,
            "trade": trade,
            "validation": validation,
        }