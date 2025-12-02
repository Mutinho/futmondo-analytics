#!/bin/bash
# Script para detener el backend

PORT=8000
PID=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PID" ]; then
    echo "✅ No hay proceso corriendo en el puerto $PORT"
else
    echo "🛑 Deteniendo proceso $PID en puerto $PORT..."
    kill $PID 2>/dev/null
    sleep 2
    
    # Si aún está corriendo, forzar
    if lsof -ti:$PORT >/dev/null 2>&1; then
        echo "⚠️  Forzando detención..."
        kill -9 $PID 2>/dev/null
        sleep 1
    fi
    
    if lsof -ti:$PORT >/dev/null 2>&1; then
        echo "❌ No se pudo detener el proceso"
    else
        echo "✅ Proceso detenido correctamente"
    fi
fi








