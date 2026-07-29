"""
Aegis AI
Module: Trading Engine
Version: 1.7.0
"""

import MetaTrader5 as mt5

from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.bias import BiasEngine
from engine.entry import EntryEngine
from engine.risk_manager import RiskManager
from engine.trade_validator import TradeValidator
from engine.trade_executor import TradeExecutor
from engine.telegram import TelegramNotifier
from engine.session_filter import SessionFilter
from engine.news_filter import NewsFilter
from engine.config import DRY_RUN
from engine.logger import logger


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

        return EntryEngine().analyze(results)



    def calculate_trade(
        self,
        analysis,
        signal,
        entry_price
    ):

        return RiskManager().calculate(
            analysis=analysis,
            signal=signal,
            entry_price=entry_price,
        )



    def validate_trade(
        self,
        analysis,
        signal
    ):

        return TradeValidator().validate(
            analysis,
            signal,
        )



    def execute_trade(
        self,
        signal,
        trade,
        validation
    ):


        if not validation["approved"]:

            TelegramNotifier().send_rejection(
                signal,
                validation["checks"],
            )

            logger.warning(
                "Trade rejected."
            )

            print(
                "\nTrade was rejected. No order created."
            )

            return



        executor = TradeExecutor()



        if executor.has_open_trade(signal):

            logger.warning(
                "Matching Aegis AI trade already exists. Skipping execution."
            )

            print(
                "\n========== TRADE GUARD ==========\n"
            )

            print(
                "⚠ Matching Aegis AI trade already exists."
            )

            print(
                "Skipping execution.\n"
            )

            return



        request = executor.build_order(
            signal,
            trade,
        )



        TelegramNotifier().send_trade(
            signal,
            trade,
        )



        if DRY_RUN:

            logger.info(
                "DRY RUN completed."
            )

            print(
                "\n========== DRY RUN COMPLETED ==========\n"
            )

            return



        result = executor.execute(
            request,
            signal,
            trade,
        )



        if result.retcode == mt5.TRADE_RETCODE_DONE:


            logger.info(
                f"Trade executed | "
                f"Retcode={result.retcode} "
                f"Order={result.order} "
                f"Deal={result.deal}"
            )


            print(
                "\n========== MT5 SUCCESS ==========\n"
            )

            print(
                f"Order : {result.order}"
            )

            print(
                f"Deal  : {result.deal}"
            )


        else:


            logger.warning(
                f"Trade failed | "
                f"Retcode={result.retcode} "
                f"Reason={result.comment}"
            )


            print(
                "\n========== MT5 FAILED ==========\n"
            )

            print(
                f"Reason : {result.comment}"
            )



    def run(self):

        try:


            logger.info(
                "Trading Engine started."
            )



            # ==========================
            # SESSION FILTER
            # ==========================

            session = SessionFilter()


            print(
                "\n========== SESSION ==========\n"
            )

            print(
                f"Current Session : {session.current_session()}"
            )


            logger.info(
                f"Current Session: {session.current_session()}"
            )


            if not session.allowed():

                print(
                    "Trading Allowed : NO"
                )

                print(
                    "Skipping trading cycle.\n"
                )


                return



            print(
                "Trading Allowed : YES"
            )



            # ==========================
            # NEWS FILTER
            # ==========================


            news = NewsFilter()


            print(
                "\n========== NEWS FILTER ==========\n"
            )


            print(
                f"Status : {news.reason()}"
            )


            logger.info(
                f"News Filter: {news.reason()}"
            )


            if not news.allowed():

                print(
                    "Trading Blocked : YES\n"
                )


                return



            print(
                "Trading Blocked : NO\n"
            )



            # ==========================
            # MARKET ANALYSIS
            # ==========================


            analysis, entry_price = self.analyze_market()



            signal = self.generate_signal(
                analysis
            )



            trade = self.calculate_trade(
                analysis,
                signal,
                entry_price,
            )



            validation = self.validate_trade(
                analysis,
                signal,
            )



            print(
                "\n========== TRADE VALIDATION ==========\n"
            )



            for check in validation["checks"]:


                clean = (
                    check.replace("✅", "[OK]")
                    .replace("❌", "[FAIL]")
                    .replace("⚠", "[WARN]")
                )


                logger.info(clean)

                print(check)



            self.execute_trade(
                signal,
                trade,
                validation,
            )



            logger.info(
                "Trading cycle completed."
            )


            return {

                "analysis": analysis,

                "signal": signal,

                "trade": trade,

                "validation": validation,

            }



        except Exception as e:


            logger.exception(
                f"Trading cycle failed: {e}"
            )


            print(
                "\n========== ERROR ==========\n"
            )

            print(e)