#!/bin/sh
# Lanzar el worker en background
python entrypoints/api/worker.py &

# Lanzar el API Flask (health y metrics) en foreground
python entrypoints/api/main.py
