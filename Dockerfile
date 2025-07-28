# Imagen base con Python 3.10
FROM python:3.10-slim

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Actualizamos y agregamos dependencias necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de la app
WORKDIR /app

# Copiar los archivos del proyecto
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Exponer puerto para Render
EXPOSE 5000

# Comando para ejecutar con Gunicorn
CMD ["gunicorn", "--bind", ":5000", "main:app"]
