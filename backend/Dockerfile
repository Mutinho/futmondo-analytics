# ===========================================
# Futmondo Analytics — Backend (FastAPI)
# ===========================================
FROM python:3.12-slim

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Instalar dependencias Python (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY run.py .

# Crear directorios necesarios
RUN mkdir -p /app/data /app/static/photos/players

# El .env se monta vía docker-compose, no se copia al imagen
# La DB SQLite se persiste en un volumen montado en /app/data/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
