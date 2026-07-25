"""
Aegis AI
Module: Risk Manager
Version: 0.2.1
"""

from engine.config import (
    ACCOUNT_BALANCE,
    RISK_PERCENT,
    RISK_REWARD,
    SL_BUFFER,
)


class RiskManager:

    def calculate(
        self,
        analysis,
        signal,
        entry_price,
        account_balance=ACCOUNT_BALANCE,
        risk_percent=RISK_PERCENT,
        rr=RISK_REWARD,
        buffer=SL_BUFFER,
    ):

        # No trade
        if signal["signal"] == "WAIT":
            return None

        # Calculate risk amount
        risk_amount = account_balance * (risk_percent / 100)
        
        # Get M15 awing data
        m15 = analysis["M15"]
        swings = m15["swings"]
        
        latest_swing_low = swings["swing_lows"][-1][1]
        latest_swing_high = swings["swing_highs"][-1][1]
        
        if signal["signal"] == "BUY":
            
            stop_loss = latest_swing_low - buffer
            sl_distance = entry_price - stop_loss
            take_profit = entry_price + (sl_distance*rr)
            
        else:
            
            stop_loss = latest_swing_high + buffer
            sl_distance = stop_loss - entry_price
            take_profit = entry_price - (sl_distance*rr)


        return {

            "entry": round(entry_price, 2),

            "stop_loss": round(stop_loss, 2),

            "take_profit": round(take_profit, 2),

            "risk_reward": f"1:{rr}",

            "lot_size": 0.10,

            "risk": round(risk_amount, 2),
        }