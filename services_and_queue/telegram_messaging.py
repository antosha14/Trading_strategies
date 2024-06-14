import requests
from celery import Celery

from data_filler.app.config import settings

celery = Celery(
    "tasks",
    broker=f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@rabbitmq:5672/{settings.RABBITMQ_DEFAULT_VHOST}",
)


@celery.task
def send_telegram_message(chat_id, message):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data).json()
