#!/bin/sh
# Lanzar el worker en background
python -m billing.entrypoints.api.worker &

# Lanzar el API Flask (health y metrics) en foreground
python -m billing.entrypoints.api.main
