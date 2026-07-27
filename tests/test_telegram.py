from engine.telegram import TelegramNotifier

message = """
🤖 AEGIS AI

✅ Telegram connection successful!

Your trading assistant is now online.
"""

result = TelegramNotifier().send(message)

print(result)