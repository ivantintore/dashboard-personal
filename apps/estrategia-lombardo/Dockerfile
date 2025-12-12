# Dockerfile para Deuda-Rentabilidad
# Compatible con dashboard-personal (ivantintore)
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema (curl para healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Puerto de la aplicación
EXPOSE 8000

# Variables de entorno para el subpath
ENV ROOT_PATH="/tools/lombardo"

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]

