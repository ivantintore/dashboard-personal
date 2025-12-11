#!/bin/bash
# ============================================
# Secret Rotation Script - Dashboard Personal
# ============================================
# This script generates new secrets and updates the .env file
# Run this quarterly or immediately if a secret is compromised
#
# Usage: ./scripts/rotate-secrets.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "   Secret Rotation - Dashboard Personal"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Please create .env from .env.example first"
    exit 1
fi

# Backup current .env
BACKUP_FILE=".env.backup.$(date +%Y%m%d_%H%M%S)"
cp .env "$BACKUP_FILE"
echo -e "${GREEN}✓${NC} Created backup: $BACKUP_FILE"

# Generate new secrets
echo ""
echo "Generating new secrets..."

NEW_AUTH_KEY=$(openssl rand -hex 64)
NEW_POSTGRES_PASS=$(openssl rand -base64 32 | tr -d '/+=')
NEW_REDIS_PASS=$(openssl rand -base64 32 | tr -d '/+=')

echo -e "${GREEN}✓${NC} Generated new AUTH_SECRET_KEY"
echo -e "${GREEN}✓${NC} Generated new POSTGRES_PASSWORD"
echo -e "${GREEN}✓${NC} Generated new REDIS_PASSWORD"

# Update .env file
echo ""
echo "Updating .env file..."

# Use sed to replace values (macOS compatible)
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s/^AUTH_SECRET_KEY=.*/AUTH_SECRET_KEY=$NEW_AUTH_KEY/" .env
    sed -i '' "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_POSTGRES_PASS/" .env
    sed -i '' "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$NEW_REDIS_PASS/" .env
else
    sed -i "s/^AUTH_SECRET_KEY=.*/AUTH_SECRET_KEY=$NEW_AUTH_KEY/" .env
    sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$NEW_POSTGRES_PASS/" .env
    sed -i "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$NEW_REDIS_PASS/" .env
fi

echo -e "${GREEN}✓${NC} Updated .env file"

# Invalidate all sessions
echo ""
echo "Invalidating all active sessions..."

if docker ps --format '{{.Names}}' | grep -q "auth-service"; then
    docker exec auth-service python -c "import database; count = database.invalidate_all_sessions(); print(f'Invalidated {count} sessions')" 2>/dev/null || echo -e "${YELLOW}Note: Could not invalidate sessions (service may not be running)${NC}"
else
    echo -e "${YELLOW}Note: auth-service container not running${NC}"
fi

# Summary
echo ""
echo "========================================"
echo -e "${GREEN}Secret rotation complete!${NC}"
echo "========================================"
echo ""
echo -e "${YELLOW}IMPORTANT: Next steps${NC}"
echo "1. Restart all services: docker-compose -f docker-compose.full.yml up -d --build"
echo "2. Verify services are healthy: docker-compose ps"
echo "3. All users will need to log in again"
echo ""
echo "Backup saved to: $BACKUP_FILE"
echo ""
