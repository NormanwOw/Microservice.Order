#!/bin/bash
set -e

if [ -f ".env-orders" ]; then
  exit 0
fi

echo "Start install..."

ORDERS_DB_NAME=orders-postgres-db
ORDERS_DB_USER=orders-postgres-user
ORDERS_DB_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9' | head -c 24)

STOCKS_DB_NAME=stocks-postgres-db
STOCKS_DB_USER=stocks-postgres-user
STOCKS_DB_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9' | head -c 24)

PAYMENTS_DB_NAME=payments-postgres-db
PAYMENTS_DB_USER=payments-postgres-user
PAYMENTS_DB_PASSWORD=$(openssl rand -base64 32 | tr -dc 'A-Za-z0-9' | head -c 24)


cat <<EOF > env-orders
DEBUG=0

DB_HOST=orders-postgres
DB_PORT=5432
POSTGRES_USER=${ORDERS_DB_USER}
POSTGRES_DB=${ORDERS_DB_NAME}
POSTGRES_PASSWORD=${ORDERS_DB_PASSWORD}

SAGA_EVENTS_TOPIC=saga.events
ORDER_COMMANDS_TOPIC=order.commands
STOCKS_COMMANDS_TOPIC=stocks.commands
PAYMENT_COMMANDS_TOPIC=payment.commands
NOTIFICATION_COMMANDS_TOPIC=notification.commands

SERVICE_NAME=order-service

KAFKA_HOSTS=["kafka:9092"]
EOF

mv -f env-orders .env-orders
chmod 600 .env-orders

cat <<EOF > env-stocks
DEBUG=0

DB_HOST=stocks-postgres
DB_PORT=5432
POSTGRES_USER=${STOCKS_DB_USER}
POSTGRES_DB=${STOCKS_DB_NAME}
POSTGRES_PASSWORD=${STOCKS_DB_PASSWORD}

STOCKS_COMMANDS_TOPIC=stocks.commands
SAGA_EVENTS_TOPIC=saga.events

KAFKA_HOSTS=["kafka:9092"]
EOF

mv -f env-stocks .env-stocks
chmod 600 .env-stocks

cat <<EOF > env-payments
DEBUG=0

DB_HOST=payment-postgres
DB_PORT=5432
POSTGRES_USER=${PAYMENTS_DB_USER}
POSTGRES_DB=${PAYMENTS_DB_NAME}
POSTGRES_PASSWORD=${PAYMENTS_DB_PASSWORD}

PAYMENT_COMMANDS_TOPIC=payment.commands
SAGA_EVENTS_TOPIC=saga.events

KAFKA_HOSTS=["kafka:9092"]
EOF

mv -f env-payments .env-payments
chmod 600 .env-payments

cat <<EOF > env-ms-orders
DB_HOST=orders-postgres
DB_PORT=5432
POSTGRES_USER=${ORDERS_DB_USER}
POSTGRES_DB=${ORDERS_DB_NAME}
POSTGRES_PASSWORD=${ORDERS_DB_PASSWORD}

KAFKA_HOSTS=["kafka:9092"]
EOF

mv -f env-ms-orders .env-ms-orders
chmod 600 .env-ms-orders

cat <<EOF > env-ms-stocks
DB_HOST=stocks-postgres
DB_PORT=5432
POSTGRES_USER=${STOCKS_DB_USER}
POSTGRES_DB=${STOCKS_DB_NAME}
POSTGRES_PASSWORD=${STOCKS_DB_PASSWORD}

KAFKA_HOSTS=["kafka:9092"]
EOF

mv -f env-ms-stocks .env-ms-stocks
chmod 600 .env-ms-stocks

cat <<EOF > env-ms-payments
DB_HOST=payment-postgres
DB_PORT=5432
POSTGRES_USER=${PAYMENTS_DB_USER}
POSTGRES_DB=${PAYMENTS_DB_NAME}
POSTGRES_PASSWORD=${PAYMENTS_DB_PASSWORD}

KAFKA_HOSTS=["kafka:9092"]
EOF

mv -f env-ms-payments .env-ms-payments
chmod 600 .env-ms-payments

docker compose -f docker-compose-kafka.yaml up -d
echo "Waiting for start up Kafka and creating topics..."
docker wait ms-kafka-init
docker rm ms-kafka-init -f
docker compose -f docker-compose-stocks.yaml up -d
docker compose -f docker-compose-orders.yaml up -d
docker compose -f docker-compose-payments.yaml up -d
echo "Install completed"




