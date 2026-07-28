from datetime import datetime

from engine.database import Database

db = Database()

db.save_trade(
    ticket=123456,
    symbol="XAUUSD",
    signal="BUY",
    volume=0.01,
    entry=4048.50,
    stop_loss=4032.50,
    take_profit=4079.50,
    confidence=70,
    status="OPEN",
    open_time=str(datetime.now()),
)

print(db.get_trade(123456))

db.close_trade(
    123456,
    profit=31.20,
    close_time=str(datetime.now()),
)

print(db.get_trade(123456))

print()

print("Total Trades:")

for trade in db.get_all_trades():
    print(trade)