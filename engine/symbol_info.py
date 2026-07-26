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

        return {
            "name": info.name,
            "point": info.point,
            "tick_size": info.trade_tick_size,
            "tick_value": info.trade_tick_value,
            "contract_size": info.trade_contract_size,
            "min_lot": info.volume_min,
            "max_lot": info.volume_max,
            "lot_step": info.volume_step,
        }