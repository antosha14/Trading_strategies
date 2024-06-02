import requests
from config import settings


# TODO: Add kafka integration for messaging
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data).json()
