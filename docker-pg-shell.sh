#!/bin/bash
# Script para acceder a PostgreSQL shell (psql)

echo "🐘 Accediendo a PostgreSQL shell..."
echo ""

# Buscar el contenedor de PostgreSQL
postgres_container=$(docker-compose ps -q postgres)

if [ -z "$postgres_container" ]; then
    echo "❌ Error: Contenedor de PostgreSQL no está corriendo"
    echo "   Ejecuta: docker-compose up -d postgres"
    exit 1
fi

# Obtener variables de entorno
POSTGRES_DB=${POSTGRES_DB:-futmondo}
POSTGRES_USER=${POSTGRES_USER:-futmondo}

echo "📊 Base de datos: $POSTGRES_DB"
echo "👤 Usuario: $POSTGRES_USER"
echo ""
echo "💡 Comandos útiles:"
echo "   \l          - Listar todas las bases de datos"
echo "   \dt        - Listar todas las tablas"
echo "   \d tabla   - Ver estructura de una tabla"
echo "   \q         - Salir"
echo ""

docker-compose exec postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"





