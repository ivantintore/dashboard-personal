#!/bin/bash
BACKUP_DIR="$HOME/dashboard-backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "💾 Creando backup en: $BACKUP_DIR"
cd "$(dirname "$0")/.."
docker-compose -f docker-compose.full.yml exec -T postgres pg_dump -U aeat_user aeat_v2 > "$BACKUP_DIR/aeat_db.sql" 2>/dev/null || echo "⚠️ PostgreSQL no disponible"
cp -r apps/*/data "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup completado: $BACKUP_DIR"
