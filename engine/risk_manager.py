"""
Aegis AI
Module: Risk Manager
Version: 0.2.1
"""

from engine.symbol_info import SymbolInfo
from engine.config import (
    ACCOUNT_BALANCE,
    RISK_PERCENT,
    RISK_REWARD,
    SL_BUFFER,
    MAX_LOT,
    MIN_LOT,
    LOT_STEP,
    
)


class RiskManager:
    
    def __init__(self):
      self.symbol = SymbolInfo()

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


        # Distance from entry to stop loss
        sl_distance = abs(entry_price - stop_loss)
        
        # Privent division by zero
        if sl_distance == 0:
            sl_distance = 0.01
            
        # Get broker symbol information
        info = self.symbol.get()

        tick_value = info["tick_value"]
        tick_size = info["tick_size"]
        min_lot = info["min_lot"]
        max_lot = info["max_lot"]
        lot_step = info["lot_step"]

        # Calculate lot size using broker data
        lot_size = risk_amount / ((sl_distance / tick_size) * tick_value)

        # Round to broker lot step
        lot_size = round(lot_size / lot_step) * lot_step

        # Apply broker limits
        lot_size = max(min_lot, lot_size)
        lot_size = min(max_lot, lot_size)


        return {

            "entry": round(entry_price, 2),

            "stop_loss": round(stop_loss, 2),

            "take_profit": round(take_profit, 2),

            "risk_reward": f"1:{rr}",

            "lot_size": round(lot_size, 2),

            "risk": round(risk_amount, 2),
        }