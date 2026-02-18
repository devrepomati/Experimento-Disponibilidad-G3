# Dockerfile para el microservicio billing

FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
COPY entrypoints/ ./entrypoints/

ENV PYTHONUNBUFFERED=1

# Comando de inicio para Flask
CMD ["python", "entrypoints/api/main.py"]