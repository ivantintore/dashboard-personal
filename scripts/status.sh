#!/bin/bash
echo "📊 Estado del Dashboard Personal"
echo "================================="
cd "$(dirname "$0")/.."
docker-compose -f docker-compose.full.yml ps
echo ""
echo "💾 Uso de volúmenes:"
docker system df -v | grep -A 20 "VOLUME NAME" | head -15
