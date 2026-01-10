#!/bin/bash
# ============================================
# 更新部署脚本（代码更新后使用）
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  ZenTea License 更新部署"
echo "=========================================="

# 加载配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
else
    echo "[ERROR] 未找到 $SCRIPT_DIR/.env，请先复制 env.example 为 .env 并配置"
    exit 1
fi

# 检查必要配置（与 deploy-all.sh 保持一致）
check_config() {
    if [ -z "$DOMAIN_API" ] || [ -z "$DOMAIN_PORTAL" ] || [ -z "$DOMAIN_ADMIN" ]; then
        echo "[ERROR] 请配置域名（DOMAIN_API/DOMAIN_PORTAL/DOMAIN_ADMIN）"
        exit 1
    fi
    if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" == "请修改为随机密钥字符串" ]; then
        echo "[ERROR] 请修改 SECRET_KEY"
        exit 1
    fi
    if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" == "请修改为强密码" ]; then
        echo "[ERROR] 请修改数据库密码"
        exit 1
    fi
    if [ -z "$ADMIN_PASSWORD" ] || [ "$ADMIN_PASSWORD" == "请修改为强密码" ]; then
        echo "[ERROR] 请在 deploy/.env 中配置 ADMIN_PASSWORD（强密码）"
        exit 1
    fi
}

# 生成/刷新后端 .env 与 docker-compose.prod.yml（保证新配置生效）
refresh_backend_compose() {
    cd "$PROJECT_DIR"

    echo "[INFO] 刷新后端配置文件..."

    # 写入后端 .env（供容器内读取 / 方便排障）
    cat > backend/.env << EOF
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
SECRET_KEY=${SECRET_KEY}
ENV=production
LICENSE_SERVER_URL=https://${DOMAIN_API}
ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
ADMIN_PASSWORD=${ADMIN_PASSWORD}
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@zentea.local}
BACKEND_CORS_ORIGINS=["http://${DOMAIN_ADMIN}","https://${DOMAIN_ADMIN}","http://${DOMAIN_PORTAL}","https://${DOMAIN_PORTAL}"]
CORS_ALLOW_CREDENTIALS=${CORS_ALLOW_CREDENTIALS:-false}
EOF

    # 写入 docker-compose.prod.yml（保持和 deploy-all.sh 一致）
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
      ENV: production
      LICENSE_SERVER_URL: https://${DOMAIN_API}
      ADMIN_USERNAME: ${ADMIN_USERNAME:-admin}
      ADMIN_PASSWORD: ${ADMIN_PASSWORD}
      ADMIN_EMAIL: ${ADMIN_EMAIL:-admin@zentea.local}
      BACKEND_CORS_ORIGINS: '["http://${DOMAIN_ADMIN}","https://${DOMAIN_ADMIN}","http://${DOMAIN_PORTAL}","https://${DOMAIN_PORTAL}"]'
      CORS_ALLOW_CREDENTIALS: "${CORS_ALLOW_CREDENTIALS:-false}"
    ports:
      - "127.0.0.1:8001:8001"
    depends_on:
      db:
        condition: service_healthy

volumes:
  postgres_data:
EOF

    echo "[INFO] 后端配置文件已刷新"
}

# 刷新 Nginx 配置（与 deploy-all.sh 保持一致，包含 docs/openapi 的拦截）
refresh_nginx_config() {
    echo "[INFO] 刷新 Nginx 配置..."

    # API 配置
    cat > /etc/nginx/conf.d/zentea-license-api.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN_API};

    # 生产环境不建议对公网暴露 FastAPI 文档/Schema（减少攻击面）
    location ~ ^/(docs|redoc|openapi\\.json)\$ {
        return 404;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

    # 管理后台配置
    cat > /etc/nginx/conf.d/zentea-license-admin.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN_ADMIN};

    root /var/www/zentea-license/admin;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        # 兜底：避免通过 /api/docs /api/openapi.json 间接访问后端文档
        location ~ ^/api/(docs|redoc|openapi\\.json)\$ {
            return 404;
        }
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

    # 用户门户配置
    cat > /etc/nginx/conf.d/zentea-license-portal.conf << EOF
server {
    listen 80;
    server_name ${DOMAIN_PORTAL};

    root /var/www/zentea-license/portal;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    location /api {
        # 兜底：避免通过 /api/docs /api/openapi.json 间接访问后端文档
        location ~ ^/api/(docs|redoc|openapi\\.json)\$ {
            return 404;
        }
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

    nginx -t
    systemctl reload nginx
    echo "[INFO] Nginx 配置已刷新"
}

cd "$PROJECT_DIR"

# 更新选项
echo "请选择更新内容："
echo "1) 仅更新后端"
echo "2) 仅更新前端"
echo "3) 全部更新"
echo "4) 退出"

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        check_config
        refresh_backend_compose
        echo "[INFO] 更新后端..."
        docker compose -f docker-compose.prod.yml build backend
        docker compose -f docker-compose.prod.yml up -d backend
        refresh_nginx_config
        echo "[INFO] 后端更新完成"
        ;;
    2)
        echo "[INFO] 更新前端..."
        
        # 管理后台
        cd "$PROJECT_DIR/frontend-admin"
        docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
            npm config set registry https://registry.npmmirror.com
            npm install --legacy-peer-deps
            npm run build
        "
        rm -rf /var/www/zentea-license/admin/*
        cp -r dist/* /var/www/zentea-license/admin/
        
        # 用户门户
        cd "$PROJECT_DIR/frontend-portal"
        docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
            npm config set registry https://registry.npmmirror.com
            npm install --legacy-peer-deps
            npm run build
        "
        rm -rf /var/www/zentea-license/portal/*
        cp -r dist/* /var/www/zentea-license/portal/
        
        echo "[INFO] 前端更新完成"
        ;;
    3)
        check_config
        refresh_backend_compose
        echo "[INFO] 更新全部..."
        
        # 后端
        docker compose -f docker-compose.prod.yml build backend
        docker compose -f docker-compose.prod.yml up -d backend
        refresh_nginx_config
        
        # 前端
        cd "$PROJECT_DIR/frontend-admin"
        docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
            npm config set registry https://registry.npmmirror.com
            npm install --legacy-peer-deps
            npm run build
        "
        rm -rf /var/www/zentea-license/admin/*
        cp -r dist/* /var/www/zentea-license/admin/
        
        cd "$PROJECT_DIR/frontend-portal"
        docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
            npm config set registry https://registry.npmmirror.com
            npm install --legacy-peer-deps
            npm run build
        "
        rm -rf /var/www/zentea-license/portal/*
        cp -r dist/* /var/www/zentea-license/portal/
        
        echo "[INFO] 全部更新完成"
        ;;
    4)
        echo "已退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  更新完成！"
echo "=========================================="

