#!/bin/bash
# Script para iniciar ngrok

echo "🌐 Iniciando ngrok para acceso público..."

# Verificar que ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok no está instalado"
    echo "📥 Instálalo desde: https://ngrok.com/download"
    echo "   O con Homebrew: brew install ngrok"
    exit 1
fi

# Verificar que el frontend está corriendo
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "⚠️  Frontend no está corriendo en puerto 3000"
    echo "   Primero ejecuta: ./start-frontend.sh"
    exit 1
fi

echo "🔗 Creando túnel público..."
echo "   Frontend local: http://localhost:3000"
echo ""
ngrok http 3000
