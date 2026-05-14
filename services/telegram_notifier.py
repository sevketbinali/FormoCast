import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    def send_message(self, message: str):
        """
        Sends a text message to the configured Telegram chat.
        """
        if not self.bot_token or not self.chat_id:
            print("Telegram settings missing. Skipping Telegram notification.")
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print("Telegram message sent.")
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

    def send_photo(self, photo_path: str, caption: str):
        """
        Sends a photo with a caption to the configured Telegram chat.
        """
        if not self.bot_token or not self.chat_id:
            return

        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        files = {'photo': open(photo_path, 'rb')}
        data = {'chat_id': self.chat_id, 'caption': caption, 'parse_mode': 'Markdown'}
        
        try:
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
            print("Telegram photo sent.")
        except Exception as e:
            print(f"Failed to send Telegram photo: {e}")
