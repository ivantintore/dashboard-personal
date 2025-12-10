#!/bin/bash
# stop-all.sh - Detiene todos los servicios del Dashboard Personal
# Uso: ./scripts/stop-all.sh

echo "🛑 Deteniendo Dashboard Personal..."
echo "================================="

cd "$(dirname "$0")/.."

docker-compose -f docker-compose.full.yml down

echo ""
echo "✅ Todos los servicios detenidos"

