from time import sleep

import requests
from app.config import settings
from services_and_queue.celery import celery


@celery.task
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data).json()
    sleep(2)
