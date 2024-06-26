#!/bin/sh
sleep 20
celery --broker=amqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@queue:5672/${RABBITMQ_DEFAULT_VHOST} flower
