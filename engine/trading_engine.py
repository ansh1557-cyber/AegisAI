"""
Aegis AI
Module: Trading Engine
Version: 1.6.1
"""


from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.bias import BiasEngine
from engine.entry import EntryEngine
from engine.risk_manager import RiskManager
from engine.trade_validator import TradeValidator
from engine.trade_executor import TradeExecutor
from engine.telegram import TelegramNotifier
from engine.session_filter import SessionFilter
from engine.news_filter import NewsFilter
from engine.trade_guard import TradeGuard
from engine.risk_validator import RiskValidator
from engine.trade_synchronizer import TradeSynchronizer

from engine.config import DRY_RUN
from engine.logger import logger



class TradingEngine:


    def analyze_market(self):

        analysis = MultiTimeframeAnalyzer().analyze()

        entry_price = (
            analysis["M15"]["data"]["close"].iloc[-1]
        )

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
            analysis,
            signal,
            entry_price
        )



    def validate_trade(
        self,
        analysis,
        signal
    ):

        return TradeValidator().validate(
            analysis,
            signal
        )



    def execute_trade(self, signal, trade, validation):


        risk_check = RiskValidator().validate(
            signal,
            trade
        )


        print("\n========== RISK CHECK ==========\n")


        for check in risk_check["checks"]:

           print(check)



        if not risk_check["approved"]:


            logger.warning(
                "Trade rejected by Risk Validator."
            )


            print(
               "\nTrade rejected by Risk Validator."
            )

            return


        guard = TradeGuard()


        if not guard.can_trade(signal):

            logger.warning(
                "Trade blocked by Trade Guard."
            )

            print(
                "\nTrade blocked by Trade Guard."
            )

            return



        if validation["approved"]:


            executor = TradeExecutor()


            if executor.has_open_trade(signal):

                logger.warning(
                    "Existing Aegis trade found."
                )

                print(
                    "\nExisting trade detected. Skipping."
                )

                return



            request = executor.build_order(
                signal,
                trade
            )


            TelegramNotifier().send_trade(
                signal,
                trade
            )


            if DRY_RUN:

                print(
                    "\n========== DRY RUN =========="
                )

                return



            result = executor.execute(
                request,
                signal,
                trade
            )


            logger.info(
                f"Trade executed | "
                f"Retcode={result.retcode}"
            )


        else:


            TelegramNotifier().send_rejection(
                signal,
                validation["checks"]
            )


            logger.warning(
                "Trade rejected."
            )



    def run(self):

        try:

            logger.info(
                "Trading Engine started."
            )
  
            TradeSynchronizer().sync()

            session = SessionFilter()


            print(
                "\n========== SESSION ==========\n"
            )

            print(
                f"Current Session : {session.current_session()}"
            )


            if not session.allowed():

                print(
                    "Trading not allowed."
                )

                return



            news = NewsFilter()


            print(
                "\n========== NEWS FILTER ==========\n"
            )

            print(
                f"Status : {news.reason()}"
            )


            if not news.allowed():

                print(
                    "Trading blocked because of news."
                )

                return



            analysis, entry_price = (
                self.analyze_market()
            )
            
            TradeSynchronizer().sync()



            signal = self.generate_signal(
                analysis
            )


            trade = self.calculate_trade(
                analysis,
                signal,
                entry_price
            )


            validation = self.validate_trade(
                analysis,
                signal
            )


            print(
                "\n========== TRADE VALIDATION ==========\n"
            )


            for check in validation["checks"]:

                print(check)


            self.execute_trade(
                signal,
                trade,
                validation
            )


            logger.info(
                "Trading cycle completed."
            )


            return {

                "analysis": analysis,

                "signal": signal,

                "trade": trade,

                "validation": validation

            }


        except Exception as e:


            logger.exception(
                f"Trading cycle failed: {e}"
            )


            print(
                "\n========== ERROR ==========\n"
            )

            print(e)