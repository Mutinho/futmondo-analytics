#!/bin/bash
# Script para ver el estado de los servicios Docker

echo "📊 Estado de los servicios Docker:"
echo ""

docker-compose ps

echo ""
echo "🔍 Estado detallado:"
echo ""

# Verificar estado de cada servicio
services=("backend" "frontend" "postgres" "pgadmin")

for service in "${services[@]}"; do
    status=$(docker-compose ps -q "$service" | xargs docker inspect -f '{{.State.Status}}' 2>/dev/null)
    if [ -z "$status" ]; then
        status="not running"
    fi
    
    if [ "$status" == "running" ]; then
        echo "   ✅ $service: $status"
    else
        echo "   ❌ $service: $status"
    fi
done

echo ""
echo "💾 Volúmenes:"
docker volume ls | grep futmondo || echo "   No hay volúmenes de Docker creados"

echo ""
echo "🌐 Redes:"
docker network ls | grep futmondo || echo "   No hay redes de Docker creadas"

