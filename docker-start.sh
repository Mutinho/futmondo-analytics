#!/bin/bash
# Script para iniciar todos los servicios Docker

echo "🐳 Iniciando servicios Docker..."

# Crear archivo .env si no existe
if [ ! -f .env ]; then
    echo "⚠️  Archivo .env no encontrado. Creando desde .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Archivo .env creado. Por favor, edítalo con tus credenciales."
        echo "   Necesitas actualizar: FUTMONDO_EMAIL y FUTMONDO_PASSWORD"
    else
        echo "❌ Error: .env.example no encontrado"
        exit 1
    fi
fi

# Construir y levantar los servicios
docker-compose up -d --build

echo ""
echo "✅ Servicios iniciados!"
echo ""
echo "📊 Servicios disponibles:"
echo "   - Backend API:    http://localhost:8000"
echo "   - Frontend:       http://localhost:3000"
echo "   - API Docs:       http://localhost:8000/docs"
echo "   - Health Check:   http://localhost:8000/health"
echo ""
echo "📝 Para ver los logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para detener los servicios:"
echo "   docker-compose down"
echo ""







