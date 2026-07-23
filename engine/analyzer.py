"""
Aegis AI
Module: Market Analyzer
Version: 0.3.3
"""

from engine.market_structure import MarketStructureEngine
from engine.structure_analyzer import StructureAnalyzer
from engine.bos import BOSEngine
from engine.choch import CHOCHEngine
from engine.fvg import FVGEngine
from engine.liquidity import LiquidityEngine
from engine.order_block import OrderBlockEngine
from engine.premium_discount import PremiumDiscountEngine


class MarketAnalyzer:

    def __init__(self):
        self.market = MarketStructureEngine()
        self.structure = StructureAnalyzer()
        self.bos = BOSEngine()
        self.choch = CHOCHEngine()
        self.fvg = FVGEngine()
        self.liquidity = LiquidityEngine()
        self.order_block = OrderBlockEngine()
        self.premium_discount = PremiumDiscountEngine()
        
    def analyze(self, df):

        print("1. Detecting swings...")
        swings = self.market.detect_swings(df)

        print("2. Analyzing structure...")
        structure = self.structure.analyze(
            swings["swing_highs"],
            swings["swing_lows"]
        )

        print("3. Detecting BOS...")
        bos = self.bos.detect(
            structure["trend"],
            swings["swing_highs"],
            swings["swing_lows"],
            df
        )

        print("4. Detecting CHoCH...")
        choch = self.choch.detect(
            structure["trend"],
            swings["swing_highs"],
            swings["swing_lows"],
            df
        )

        print("5. Detecting FVG...")
        fvg = self.fvg.detect(df)

        print("6. Detecting Liquidity...")
        liquidity = self.liquidity.detect(
            df,
            swings["swing_highs"],
            swings["swing_lows"]
        )
        
        print("7. Detecting Order Blocks...")
        order_blocks = self.order_block.detect(df)
        
        print("8. Detecting Premium / Discount Zones...")

        premium_discount = self.premium_discount.detect(  
            df,                                            
            swings["swing_highs"],
            swings["swing_lows"]
        )

        print("8. Analysis complete!")

        return {
            "swings": swings,
            "structure": structure,
            "bos": bos,
            "choch": choch,
            "fvg": fvg,
            "liquidity": liquidity,
            "order_blocks": order_blocks,
            "premium_discount": premium_discount,
        }