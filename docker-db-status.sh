#!/bin/bash
# Script para ver el estado de la base de datos PostgreSQL

echo "🗄️  Estado de la base de datos PostgreSQL"
echo ""

# Verificar si PostgreSQL está corriendo
postgres_container=$(docker-compose ps -q postgres)

if [ -z "$postgres_container" ]; then
    echo "❌ PostgreSQL no está corriendo"
    echo "   Ejecuta: docker-compose up -d postgres"
    exit 1
fi

echo "✅ PostgreSQL está corriendo"
echo ""

# Mostrar información del contenedor
echo "📊 Información del contenedor:"
docker-compose ps postgres

echo ""
echo "📈 Estadísticas:"
docker stats --no-stream futmondo-postgres

echo ""
echo "💾 Volumen de datos:"
docker volume inspect futmondoapi_postgres-data 2>/dev/null | grep -A 5 "Mountpoint" || echo "   Volumen no encontrado"

echo ""
echo "🔍 Para ver los logs:"
echo "   ./docker-logs.sh postgres"

echo ""
echo "🌐 Para acceder a pgAdmin:"
echo "   http://localhost:5050"
echo "   Email: admin@futmondo.com"
echo "   Password: admin123 (o el configurado en .env)"





