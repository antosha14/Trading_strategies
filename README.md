# Data gathering / Trading application for Bitcoin on Binance

## Be careful, current strategy makes huge LOSSES!!
### Configuration is done by ./app/.env

_Primary configuration_
Your .env file should contain this data: 
```
PROJECT_NAME=

POSTGRES_SERVER=
POSTGRES_PORT=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

PGDATA=

RABBIT_DOMAIN=
RABBITMQ_DEFAULT_USER=
RABBITMQ_DEFAULT_PASS=
RABBITMQ_DEFAULT_VHOST=

DOCKER_IMAGE_GATHERING=
DOMAIN=
SMTP_HOST=
ENVIRONMENT=

SECRET_KEY=
TELEGRAM_CHAT_ID=
TELEGRAM_BOT_TOKEN=

FIRST_SUPERUSER=
FIRST_SUPERUSER_PASSWORD=
BINANCE_API_KEY=
BINANCE_API_SECRET=
```

### In order to run the app you need to have docker installed. Then you can launch the app with
```
docker compose up
```