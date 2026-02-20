#!/bin/sh
# Esperar a que Kafka esté disponible
python /app/payments/wait_for_kafka.py

# Lanzar el worker en background
python /app/payments/entrypoints/api/worker.py &

# Lanzar el API Flask (health y metrics) en foreground
python /app/payments/entrypoints/api/main.py