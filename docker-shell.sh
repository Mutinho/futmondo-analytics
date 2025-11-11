#!/bin/bash
# Script para acceder al shell de un servicio Docker

if [ -z "$1" ]; then
    echo "Uso: ./docker-shell.sh [backend|frontend]"
    echo ""
    echo "Ejemplos:"
    echo "  ./docker-shell.sh backend   # Acceder al shell del backend"
    echo "  ./docker-shell.sh frontend  # Acceder al shell del frontend"
    exit 1
fi

service=$1

echo "🐚 Accediendo al shell del servicio: $service"
echo ""

docker-compose exec "$service" /bin/sh || docker-compose exec "$service" /bin/bash





