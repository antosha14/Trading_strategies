from app.config import settings
from celery import Celery

celery = Celery(
    "services_and_queue",
    broker=f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@127.0.0.1:5672/{settings.RABBITMQ_DEFAULT_VHOST}",
)

if __name__ == "__main__":
    celery.start()
