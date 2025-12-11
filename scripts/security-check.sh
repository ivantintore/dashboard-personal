#!/bin/bash
# ============================================
# Security Check Script - Dashboard Personal
# ============================================
# Run this before deploying to verify security configuration
#
# Usage: ./scripts/security-check.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo "========================================"
echo "   Security Check - Dashboard Personal"
echo "========================================"
echo ""

# Check .env exists and has required vars
echo "Checking environment configuration..."

if [ ! -f ".env" ]; then
    echo -e "${RED}✗${NC} .env file not found"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check required variables
    source .env 2>/dev/null || true
    
    if [ -z "$AUTH_SECRET_KEY" ] || [ "$AUTH_SECRET_KEY" == "generate-with-openssl-rand-hex-64" ]; then
        echo -e "${RED}✗${NC} AUTH_SECRET_KEY not set or using default"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓${NC} AUTH_SECRET_KEY is set"
    fi
    
    if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" == "generate-secure-password" ]; then
        echo -e "${RED}✗${NC} POSTGRES_PASSWORD not set or using default"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓${NC} POSTGRES_PASSWORD is set"
    fi
    
    if [ -z "$GOOGLE_CLIENT_ID" ]; then
        echo -e "${RED}✗${NC} GOOGLE_CLIENT_ID not set"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓${NC} GOOGLE_CLIENT_ID is set"
    fi
    
    if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
        echo -e "${RED}✗${NC} GOOGLE_CLIENT_SECRET not set"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "${GREEN}✓${NC} GOOGLE_CLIENT_SECRET is set"
    fi
    
    if [ -z "$ADMIN_EMAIL" ]; then
        echo -e "${YELLOW}!${NC} ADMIN_EMAIL not set (optional but recommended)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✓${NC} ADMIN_EMAIL is set"
    fi
fi

echo ""
echo "Checking for exposed secrets in codebase..."

# Check for hardcoded passwords
if grep -r "password.*=.*['\"]" --include="*.py" --include="*.yml" --include="*.yaml" . 2>/dev/null | grep -v ".env" | grep -v "example" | grep -v "PASSWORD}" | head -5; then
    echo -e "${YELLOW}!${NC} Possible hardcoded passwords found (review above)"
    WARNINGS=$((WARNINGS + 1))
else
    echo -e "${GREEN}✓${NC} No obvious hardcoded passwords"
fi

# Check for sensitive files not in gitignore
echo ""
echo "Checking .gitignore..."

if grep -q "client_secret" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✓${NC} client_secret files are gitignored"
else
    echo -e "${YELLOW}!${NC} client_secret files should be in .gitignore"
    WARNINGS=$((WARNINGS + 1))
fi

if grep -q "\.env" .gitignore 2>/dev/null; then
    echo -e "${GREEN}✓${NC} .env files are gitignored"
else
    echo -e "${RED}✗${NC} .env files should be in .gitignore"
    ERRORS=$((ERRORS + 1))
fi

# Check for sensitive files in repo
echo ""
echo "Checking for sensitive files..."

if ls client_secret*.json 2>/dev/null; then
    echo -e "${RED}✗${NC} client_secret*.json files found in repo - REMOVE THEM"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} No client_secret files in repo"
fi

# Check Docker configuration
echo ""
echo "Checking Docker configuration..."

if grep -q "AUTH_SECRET_KEY:-supersecretkey123" docker-compose.full.yml 2>/dev/null; then
    echo -e "${RED}✗${NC} Insecure default SECRET_KEY in docker-compose"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} No insecure default secrets in docker-compose"
fi

if grep -q "POSTGRES_PASSWORD:.*aeat_pass" docker-compose.full.yml 2>/dev/null; then
    echo -e "${RED}✗${NC} Hardcoded Postgres password in docker-compose"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} Postgres password uses environment variable"
fi

# Summary
echo ""
echo "========================================"
echo "   Security Check Summary"
echo "========================================"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}All checks passed! ✓${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}Passed with $WARNINGS warning(s)${NC}"
    exit 0
else
    echo -e "${RED}Failed with $ERRORS error(s) and $WARNINGS warning(s)${NC}"
    echo ""
    echo "Please fix the errors before deploying to production."
    exit 1
fi
