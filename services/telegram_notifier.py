import requests
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not self.bot_token or not self.chat_id:
            print("Telegram credentials missing. Telegram notifications disabled.")

    def send_message(self, message: str):
        if not self.bot_token or not self.chat_id:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Telegram error: {e}")

    def send_photo(self, photo_path: str, caption: str = None):
        if not self.bot_token or not self.chat_id:
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
        try:
            with open(photo_path, 'rb') as photo:
                files = {"photo": photo}
                payload = {"chat_id": self.chat_id, "caption": caption, "parse_mode": "Markdown"}
                requests.post(url, files=files, data=payload)
        except Exception as e:
            print(f"Telegram photo error: {e}")
