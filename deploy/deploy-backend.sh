#!/bin/bash
# ============================================
# 仅部署后端（前后端分离时使用）
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  ZenTea License 后端部署"
echo "=========================================="

# 加载配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
else
    echo "[ERROR] 请先复制 env.example 为 .env 并配置"
    exit 1
fi

cd "$PROJECT_DIR"

# 创建 docker-compose 配置
cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: zentea-license-db
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: zentea-license-backend
    restart: always
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      SECRET_KEY: ${SECRET_KEY}
      LICENSE_SERVER_URL: https://${DOMAIN_API}
    ports:
      - "0.0.0.0:8001:8001"
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
EOF

# 构建并启动
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo ""
echo "=========================================="
echo "  后端部署完成！"
echo "=========================================="
echo ""
echo "API 地址: http://$(hostname -I | awk '{print $1}'):8001"
echo "API 文档: http://$(hostname -I | awk '{print $1}'):8001/docs"
echo ""
echo "前端配置时，请将 API 地址设置为上述地址"
echo ""

