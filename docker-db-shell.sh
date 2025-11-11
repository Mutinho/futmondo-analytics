#!/bin/bash
# Script para acceder a la base de datos SQLite

echo "🗄️  Accediendo a la base de datos SQLite..."

# Buscar el contenedor del backend
backend_container=$(docker-compose ps -q backend)

if [ -z "$backend_container" ]; then
    echo "❌ Error: Contenedor del backend no está corriendo"
    echo "   Ejecuta: docker-compose up -d"
    exit 1
fi

# Verificar si la base de datos existe
db_path="/app/data/futmondo_data.db"

if ! docker-compose exec backend test -f "$db_path"; then
    echo "⚠️  Base de datos no encontrada en: $db_path"
    echo "   Se creará automáticamente cuando el backend se inicie"
    exit 1
fi

echo "📊 Abriendo SQLite shell..."
echo "   Base de datos: $db_path"
echo ""
echo "💡 Comandos útiles:"
echo "   .tables          - Ver todas las tablas"
echo "   .schema          - Ver el esquema de la base de datos"
echo "   SELECT * FROM players LIMIT 10;"
echo ""

docker-compose exec backend sqlite3 "$db_path"





