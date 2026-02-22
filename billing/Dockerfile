# Dockerfile para el microservicio billing

FROM python:3.11-slim

# Crear carpeta billing dentro de /app
WORKDIR /app/billing

# Copiar archivos de requerimientos
COPY requirements.txt /app/billing/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente dentro de billing
COPY adapters /app/billing/adapters
COPY application /app/billing/application
COPY domain /app/billing/domain
COPY entrypoints /app/billing/entrypoints
COPY infrastructure /app/billing/infrastructure
COPY wait_for_kafka.py /app/billing/wait_for_kafka.py

# Dar permisos de ejecución al script de inicio
RUN chmod +x /app/billing/entrypoints/api/start.sh

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV VOTING_ENABLED=1

# Comando de inicio para Flask y worker
CMD ["sh", "entrypoints/api/start.sh"]
