# Imagen base con VERSIÓN FIJA (requisito del paso 2: no usar "latest").
FROM python:3.12-slim

# Evita que Python escriba archivos .pyc dentro del contenedor.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Primero las dependencias: aprovecha la caché de capas de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Después el código de la aplicación.
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
