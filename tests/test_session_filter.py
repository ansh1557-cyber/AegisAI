from engine.session_filter import SessionFilter

session = SessionFilter()

print("Current Session :", session.current_session())
print("Trading Allowed :", session.allowed())