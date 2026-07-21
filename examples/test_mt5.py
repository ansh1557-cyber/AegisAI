from engine.mt5_connector import MT5Connector

connector = MT5Connector()

connector.connect()

df = connector.get_rates()

print(df.head())
print()
print(df.tail())

connector.disconnect()