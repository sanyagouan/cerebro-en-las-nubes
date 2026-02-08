#!/bin/bash
# Script de deployment manual para Coolify
# Uso: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
echo "🚀 Deploying to $ENVIRONMENT..."

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar variables de entorno
if [ -z "$COOLIFY_API_TOKEN" ]; then
    echo -e "${RED}❌ Error: COOLIFY_API_TOKEN no está configurado${NC}"
    exit 1
fi

if [ -z "$COOLIFY_INSTANCE" ]; then
    echo -e "${RED}❌ Error: COOLIFY_INSTANCE no está configurado${NC}"
    exit 1
fi

# Build Docker image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build -t en-las-nubes-backend:latest .

# Verificar health localmente
echo -e "${YELLOW}🔍 Running health check locally...${NC}"
docker run -d --name test-backend -p 8000:8000 en-las-nubes-backend:latest
sleep 10

if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    docker logs test-backend
    docker stop test-backend && docker rm test-backend
    exit 1
fi

docker stop test-backend && docker rm test-backend

# Trigger deployment en Coolify
echo -e "${YELLOW}🚀 Triggering Coolify deployment...${NC}"

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "https://$COOLIFY_INSTANCE/api/v1/deploy" \
    -H "Authorization: Bearer $COOLIFY_API_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"project\": \"en-las-nubes\",
        \"service\": \"cerebro-backend\",
        \"environment\": \"$ENVIRONMENT\"
    }")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 202 ]; then
    echo -e "${GREEN}✅ Deployment triggered successfully!${NC}"
    echo "Response: $BODY"
else
    echo -e "${RED}❌ Deployment failed with HTTP $HTTP_CODE${NC}"
    echo "Response: $BODY"
    exit 1
fi

# Esperar y verificar deployment
echo -e "${YELLOW}⏳ Waiting for deployment to complete...${NC}"
sleep 30

echo -e "${GREEN}✅ Deployment completed!${NC}"
echo ""
echo "📊 Check status at: https://$COOLIFY_INSTANCE/projects/en-las-nubes"
