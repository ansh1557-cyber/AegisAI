"""
Aegis AI
Module: Telegram Notifications
Version: 0.2.0
"""

import requests

from engine.telegram_config import BOT_TOKEN, CHAT_ID


class TelegramNotifier:

    def send(self, message):

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        payload = {
            "chat_id": CHAT_ID,
            "text": message,
        }

        response = requests.post(url, data=payload)

        return response.json()

    def send_trade(self, signal, trade):

        message = f"""
🤖 AEGIS AI

🟢 {signal['signal']} SIGNAL

Symbol: XAUUSD

Entry: {trade['entry']}
Stop Loss: {trade['stop_loss']}
Take Profit: {trade['take_profit']}

Risk : Reward: {trade['risk_reward']}
Lot Size: {trade['lot_size']}

Confidence: {signal['confidence']}%

Reasons:
"""

        for reason in signal["reasons"]:
            message += f"\n✓ {reason}"
            
    def send_rejection(self, signal, checks):

        message = f"""
    🤖 AEGIS AI

    ❌ TRADE REJECTED

    Signal: {signal['signal']}

    Validation:
    """

        for check in checks:
            message += f"\n{check}"

        return self.send(message)