# Dockerfile para el componente de monitoreo

FROM python:3.11-slim

WORKDIR /app

# Copiar archivos de requerimientos si aplica
COPY requirements.txt .

# Instalar dependencias (descomente si usa requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "main.py"]
