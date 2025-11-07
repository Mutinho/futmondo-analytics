#!/bin/bash
# Script para iniciar el frontend

echo "🚀 Iniciando Futmondo Frontend..."
cd frontend

# Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias..."
    npm install
fi

echo "🔥 Iniciando servidor en http://localhost:3000"
npm start
