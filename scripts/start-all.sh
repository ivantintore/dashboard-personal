#!/bin/bash
# start-all.sh - Inicia todos los servicios del Dashboard Personal
# Uso: ./scripts/start-all.sh

set -e

echo "🚀 Iniciando Dashboard Personal..."
echo "================================="

cd "$(dirname "$0")/.."

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Iniciar con docker-compose.full.yml
echo "📦 Construyendo e iniciando contenedores..."
docker-compose -f docker-compose.full.yml up -d --build

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar health
echo ""
echo "✅ Estado de los servicios:"
docker-compose -f docker-compose.full.yml ps

echo ""
echo "================================="
echo "🎉 Dashboard Personal iniciado!"
echo ""
echo "📌 Accesos:"
echo "   Dashboard:    http://localhost"
echo "   Conversor:    http://localhost/conversor/"
echo "   AEAT API:     http://localhost/aeat/"
echo "   AEAT UI:      http://localhost/aeat-ui/"
echo "   Intrastat:    http://localhost/intrastat/"
echo "   Taxi:         http://localhost/taxi/"
echo "   Adela:        http://localhost/adela/"
echo "   Toroidal:     http://localhost/toroidal/"
echo "   Flower:       http://localhost/flower/"
echo ""
echo "🔐 Login: admin / demo123"
echo "================================="


