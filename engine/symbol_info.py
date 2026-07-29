"""
Aegis AI
Module: Symbol Information
Version: 0.1.0
"""

import MetaTrader5 as mt5
from engine.config import SYMBOL


class SymbolInfo:

    def get(self):

        info = mt5.symbol_info(SYMBOL)

        if info is None:
            raise Exception(f"Could not load symbol information for {SYMBOL}")
        
        tick = mt5.symbol_info_tick(SYMBOL)
            

        return {
            "name": info.name,

            # Price information
            "point": info.point,
            "tick_size": info.trade_tick_size,
            "tick_value": info.trade_tick_value,

            # Contract
            "contract_size": info.trade_contract_size,

            # Volume rules
            "min_lot": info.volume_min,
            "max_lot": info.volume_max,
            "lot_step": info.volume_step,

            # Trading restrictions
            "stops_level": info.trade_stops_level,
            "freeze_level": info.trade_freeze_level,

            # Market conditions
            "spread": info.spread,
            "bid" : tick.bid,
            "ask" : tick.ask,
}