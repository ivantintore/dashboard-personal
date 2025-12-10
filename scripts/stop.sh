#!/bin/bash
# Stop PoC Dashboard

echo "🛑 Deteniendo PoC Dashboard..."

cd "$(dirname "$0")/.."

docker-compose down

echo "✅ Dashboard detenido"
