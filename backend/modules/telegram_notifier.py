"""
Telegram Bot Notification Engine
Sends high-conviction trade alerts to your personal Telegram account.
"""

import os
import requests
import time
from dotenv import load_dotenv
from modules.logger import app_logger

# Load environment variables from .env
load_dotenv()

# Load credentials from environment or config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

class TelegramNotifier:
    def __init__(self):
        self.bot_token = TELEGRAM_BOT_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            app_logger.warning("Telegram Bot is disabled. Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables.")
        else:
            app_logger.info("Telegram Bot Notifier is active.")

    def send_alert(self, symbol: str, direction: str, cmp: float, target: float, sl: float, triggers: list, score: int):
        """Sends a formatted trade alert to Telegram."""
        if not self.enabled:
            return False
            
        emoji = "🟢 LONG" if direction == "LONG" else "🔴 SHORT"
        trigger_text = "\n".join([f"✅ {t}" for t in triggers])
        
        message = f"""
🚨 <b>NSE AI ALERT: {symbol}</b>
{emoji} @ ₹{cmp} | Score: {score}/100

<b>Targets & Risk:</b>
🎯 TGT 1: ₹{target}
🛑 SL: ₹{sl}

<b>Confluence Triggers:</b>
{trigger_text}

<i>Sent by NSE AI Trading Stack</i>
"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                app_logger.info(f"Telegram alert sent successfully for {symbol}")
                return True
            else:
                app_logger.error(f"Failed to send Telegram alert: {response.text}")
                return False
        except Exception as e:
            app_logger.error(f"Telegram connection error: {e}")
            return False

# Singleton instance
telegram_notifier = TelegramNotifier()
