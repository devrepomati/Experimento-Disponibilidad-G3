# Dockerfile para el microservicio reservas

FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script de espera a la raíz de trabajo
COPY wait_for_kafka.py /app/wait_for_kafka.py

# Copiar el resto del código fuente como paquete
COPY . /app/reservas

ENV PYTHONUNBUFFERED=1

# Comando de inicio: esperar a Kafka y luego iniciar Flask
CMD ["sh", "-c", "python wait_for_kafka.py && python -m reservas.entrypoints.api.main"]
