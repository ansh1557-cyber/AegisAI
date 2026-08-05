"""
Aegis AI
Module: ATR Indicator
Version: 0.1.0
"""

import pandas as pd


class ATRIndicator:

    def __init__(self, period=14):
        self.period = period

    # Convert column names to lowercase
    def calculate(self, df):
        
      
         # Convert column names to lowercase
        df = df.rename(columns=str.lower)
        
        # Check that required columns exist
        required = ["high", "low", "close"]  
        
        for column in required:
            if column not in df.columns:
                raise ValueError(f"Missing column: {column}")
            
        # Check that there are enough candles
        if len(df) < self.period:
            return None
        
         # Get OHLC data
        high = df["high"]
        low = df["low"]
        close = df["close"]

        tr = pd.concat(
            [
                high - low,
                (high - close.shift()).abs(),
                (low - close.shift()).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr = tr.rolling(self.period).mean()
        
        if pd.isna(atr.iloc[-1]):
            return None

        return float(atr.iloc[-1])