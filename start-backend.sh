#!/bin/bash
# Script para iniciar el backend

echo "🚀 Iniciando Futmondo Backend..."

# Verificar y detener proceso que esté usando el puerto 8000
PORT=8001
PID=$(lsof -ti:$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "⚠️  Puerto $PORT está en uso por el proceso $PID"
    echo "🛑 Deteniendo proceso anterior..."
    kill $PID 2>/dev/null
    sleep 2
    # Verificar si se detuvo
    if lsof -ti:$PORT >/dev/null 2>&1; then
        echo "⚠️  No se pudo detener el proceso. Forzando..."
        kill -9 $PID 2>/dev/null
        sleep 1
    fi
    echo "✅ Puerto $PORT liberado"
fi

cd backend

# Activar venv si existe
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "⚠️  Creando entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Instalando dependencias..."
    pip install -r requirements.txt
fi

echo "🔥 Iniciando servidor en http://localhost:$PORT"
python run.py
