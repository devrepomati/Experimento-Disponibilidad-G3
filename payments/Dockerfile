# Dockerfile para el microservicio payments

FROM python:3.11-slim

WORKDIR /app/payments

# Copiar archivos de requerimientos
COPY requirements.txt /app/payments/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente dentro de payments
COPY adapters /app/payments/adapters
COPY application /app/payments/application
COPY domain /app/payments/domain
COPY entrypoints /app/payments/entrypoints
COPY infrastructure /app/payments/infrastructure
COPY wait_for_kafka.py /app/payments/wait_for_kafka.py

# Dar permisos de ejecución al script de inicio
RUN chmod +x /app/payments/entrypoints/api/start.sh

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Comando de inicio para Flask y worker
CMD ["sh", "entrypoints/api/start.sh"]
