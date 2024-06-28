from app.config import settings
from celery import Celery

# TODO: change IP to config, dependable on environment (test, production)
celery = Celery(
    "services_and_queue",
    broker=f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@queue:5672/{settings.RABBITMQ_DEFAULT_VHOST}",
    include=["services_and_queue.telegram_messaging"],
)

if __name__ == "__main__":
    celery.start()
