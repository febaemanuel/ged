#!/bin/bash
set -e
echo "🚀 Deploy GED EBSERH"
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Execute como root: sudo ./deploy.sh${NC}"
    exit 1
fi

echo "1️⃣  Verificando Docker..."
docker --version || exit 1
echo -e "${GREEN}✅ Docker OK${NC}"

echo "2️⃣  Verificando .env..."
[ -f .env ] || { echo -e "${RED}❌ .env não encontrado${NC}"; exit 1; }
echo -e "${GREEN}✅ .env OK${NC}"

echo "3️⃣  Build..."
docker compose build

echo "4️⃣  Deploy..."
docker compose down 2>/dev/null || true
docker compose up -d

echo "5️⃣  Aguardando..."
sleep 10

echo "6️⃣  Health check..."
curl -sf http://localhost:5000/health | jq . || curl -s http://localhost:5000/health

echo -e "${GREEN}✅ DEPLOY CONCLUÍDO!${NC}"
