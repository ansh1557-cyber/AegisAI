"""
Aegis AI
Module: Telegram Notifications
Version: 0.3.0
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

        return self.send(message)

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

    def send_trade_opened(self, position):

        message = (
            "🤖 AEGIS AI\n\n"
            "🟢 TRADE OPENED\n\n"
            f"Symbol: {position.symbol}\n"
            f"Type: {'BUY' if position.type == 0 else 'SELL'}\n"
            f"Volume: {position.volume}\n\n"
            f"Entry: {position.price_open}\n"
            f"SL: {position.sl}\n"
            f"TP: {position.tp}"
        )

        return self.send(message)

    def send_trade_closed(self, ticket, deal=None):
        
        if deal is None:

            message = (
                "🤖 AEGIS AI\n\n"
                "🔴 TRADE CLOSED\n\n"
                f"Ticket: {ticket}"
            )
        else:

            if deal.profit > 0:
                status = "🎯 TAKE PROFIT"
            elif deal.profit < 0:
                status = "🛑 STOP LOSS"
            else:
                status = "⚪ BREAKEVEN"

        message = (
            f"🤖 AEGIS AI\n\n"
            f"{status}\n\n"
            f"Ticket: {ticket}\n"
            f"Profit: {deal.profit:.2f}\n"
            f"Close Price: {deal.price}"
        )

        return self.send(message)