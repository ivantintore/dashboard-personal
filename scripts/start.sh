#!/bin/bash
# Start PoC Dashboard

echo "🚀 Iniciando PoC Dashboard Personal..."
echo ""

cd "$(dirname "$0")/.."

# Build and start
docker-compose up -d --build

echo ""
echo "✅ Dashboard iniciado!"
echo ""
echo "📍 Acceso: http://localhost"
echo "👤 Usuario: admin"
echo "🔑 Password: demo123"
echo ""
echo "📊 Ver logs: docker-compose logs -f"
echo "🛑 Detener: ./scripts/stop.sh"
