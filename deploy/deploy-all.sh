#!/bin/bash
# ============================================
# 单服务器全量部署脚本
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  ZenTea License 全量部署"
echo "=========================================="

# 加载配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
else
    echo "[ERROR] 请先复制 env.example 为 .env 并配置"
    exit 1
fi

# 检查必要配置
check_config() {
    if [ -z "$DOMAIN_API" ] || [ -z "$DOMAIN_PORTAL" ] || [ -z "$DOMAIN_ADMIN" ]; then
        echo "[ERROR] 请配置域名"
        exit 1
    fi
    
    if [ "$SECRET_KEY" == "请修改为随机密钥字符串" ]; then
        echo "[ERROR] 请修改 SECRET_KEY"
        exit 1
    fi
    
    if [ "$POSTGRES_PASSWORD" == "请修改为强密码" ]; then
        echo "[ERROR] 请修改数据库密码"
        exit 1
    fi

    if [ -z "$ADMIN_PASSWORD" ] || [ "$ADMIN_PASSWORD" == "请修改为强密码" ]; then
        echo "[ERROR] 请在 deploy/.env 中配置 ADMIN_PASSWORD（强密码）"
        exit 1
    fi
}

# 部署后端
deploy_backend() {
    echo "[INFO] 部署后端服务..."
    
    cd "$PROJECT_DIR"
    
    # 创建 .env 文件
    cat > backend/.env << EOF
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
SECRET_KEY=${SECRET_KEY}
# 生产环境
ENV=production
# 对外授权 API 基地址（供 ERP/APP 调用）
LICENSE_SERVER_URL=https://${DOMAIN_API}
# 初始化管理员（首次启动会创建）
ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
ADMIN_PASSWORD=${ADMIN_PASSWORD}
ADMIN_EMAIL=${ADMIN_EMAIL:-admin@zentea.local}
# CORS 白名单：允许 portal/admin 域名访问后端（含 http/https，便于先 HTTP 部署再上 HTTPS）
BACKEND_CORS_ORIGINS=["http://${DOMAIN_ADMIN}","https://${DOMAIN_ADMIN}","http://${DOMAIN_PORTAL}","https://${DOMAIN_PORTAL}"]
CORS_ALLOW_CREDENTIALS=${CORS_ALLOW_CREDENTIALS:-false}
EOF
    
    # 创建生产用 docker-compose
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
    
    # 构建并启动
    docker compose -f docker-compose.prod.yml build
    docker compose -f docker-compose.prod.yml up -d
    
    echo "[INFO] 后端服务部署完成"
}

# 构建前端
build_frontend() {
    echo "[INFO] 构建前端..."
    
    cd "$PROJECT_DIR"
    
    # 确保目标目录存在
    mkdir -p /var/www/zentea-license/admin
    mkdir -p /var/www/zentea-license/portal
    
    # 构建管理后台
    echo "[INFO] 构建管理后台..."
    cd "$PROJECT_DIR/frontend-admin"
    
    # 使用 Docker 构建（避免本地 Node 环境问题）
    docker run --rm -v "$PWD":/app -w /app node:20-alpine sh -c "
        rm -rf node_modules
        npm config set registry https://registry.npmmirror.com
        npm install --legacy-peer-deps
        npm run build
    "
    
    # 检查构建是否成功
    if [ ! -d "dist" ]; then
        echo "[ERROR] 管理后台构建失败"
        exit 1
    fi
    
    # 复制构建产物
    rm -rf /var/www/zentea-license/admin/*
    cp -r dist/* /var/www/zentea-license/admin/
    
    # 构建用户门户
    echo "[INFO] 构建用户门户..."
    cd "$PROJECT_DIR/frontend-portal"
    
    docker run --rm -v "$PWD":/app -w /app node:20-alpine sh -c "
        rm -rf node_modules
        npm config set registry https://registry.npmmirror.com
        npm install --legacy-peer-deps
        npm run build
    "
    
    # 检查构建是否成功
    if [ ! -d "dist" ]; then
        echo "[ERROR] 用户门户构建失败"
        exit 1
    fi
    
    # 复制构建产物
    rm -rf /var/www/zentea-license/portal/*
    cp -r dist/* /var/www/zentea-license/portal/
    
    echo "[INFO] 前端构建完成"
}

# 配置 Nginx
configure_nginx() {
    echo "[INFO] 配置 Nginx..."
    
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
    
    # 测试配置
    nginx -t
    
    # 重载 Nginx
    systemctl reload nginx
    
    echo "[INFO] Nginx 配置完成"
}

# 主函数
main() {
    check_config
    deploy_backend
    build_frontend
    configure_nginx
    
    echo ""
    echo "=========================================="
    echo "  部署完成！"
    echo "=========================================="
    echo ""
    echo "服务地址（HTTP）："
    echo "  API: http://${DOMAIN_API}"
    echo "  管理后台: http://${DOMAIN_ADMIN}"
    echo "  用户门户: http://${DOMAIN_PORTAL}"
    echo ""
    echo "管理员账号: ${ADMIN_USERNAME:-admin}"
    echo "管理员密码: （使用 deploy/.env 中配置的 ADMIN_PASSWORD；生产环境不建议使用弱密码）"
    echo ""
    echo "下一步: 运行 ./setup-ssl.sh 配置 HTTPS"
    echo ""
}

main

