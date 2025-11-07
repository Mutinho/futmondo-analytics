#!/bin/bash
# Script para ver los logs de los servicios Docker

# Si se proporciona un servicio específico, mostrar solo sus logs
if [ -n "$1" ]; then
    echo "📋 Mostrando logs de: $1"
    docker-compose logs -f "$1"
else
    echo "📋 Mostrando logs de todos los servicios"
    docker-compose logs -f
fi

