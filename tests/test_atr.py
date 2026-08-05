from engine.mt5_connector import MT5Connector
from engine.atr import ATRIndicator
from engine.config import SYMBOL
import MetaTrader5 as mt5

connector = MT5Connector()
connector.connect()

df = connector.get_rates(
    symbol=SYMBOL,
    timeframe=mt5.TIMEFRAME_M15,
    bars=200,
)

print(df.columns)
print(df.head())

atr = ATRIndicator()

value = atr.calculate(df)

print("\n========== ATR TEST ==========\n")
print(f"ATR Value : {value:.2f}")