import requests
import os
from datetime import datetime
from config import MARKET_TIMEZONE

class TelegramAlerts:
    """Send alerts to Telegram bot"""
    
    def __init__(self, token=None, chat_id=None):
        self.token = token or os.getenv("TELEGRAM_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = self.token is not None and self.chat_id is not None
        
    def send_message(self, message):
        """Send a text message to Telegram"""
        if not self.enabled:
            print(f"Telegram Alert (Disabled): {message}")
            return False
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")
            return False
            
    def alert_trade(self, signal, symbol, price, sl, target):
        """Send a trade alert message"""
        now = datetime.now(MARKET_TIMEZONE).strftime("%H:%M:%S")
        emoji = "🚀" if signal == "BUY" else "🔻"
        message = (
            f"{emoji} *{signal} SIGNAL* {emoji}\n\n"
            f"*Symbol:* {symbol}\n"
            f"*Price:* ₹{price}\n"
            f"*SL:* ₹{sl}\n"
            f"*Target:* ₹{target}\n"
            f"*Time:* {now}"
        )
        return self.send_message(message)
