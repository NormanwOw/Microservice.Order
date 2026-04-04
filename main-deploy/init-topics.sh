#!/bin/bash
set -e

while ! nc -z kafka 9092; do
  sleep 1
done

sleep 5

TOPICS=(
  "order.commands"
  "payment.commands"
  "stocks.commands"
  "notification.commands"
  "saga.events"
)

for TOPIC in "${TOPICS[@]}"; do
  until /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list | grep -Fxq "${TOPIC}"; do
    /opt/kafka/bin/kafka-topics.sh --create \
      --bootstrap-server kafka:9092 \
      --replication-factor 1 \
      --partitions 3 \
      --topic "${TOPIC}"
    sleep 1
  done
done