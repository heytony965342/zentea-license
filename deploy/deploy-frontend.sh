#!/bin/bash
# ============================================
# 仅部署前端（前后端分离时使用）
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  ZenTea License 前端部署"
echo "=========================================="

# 加载配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
else
    echo "[ERROR] 请先复制 env.example 为 .env 并配置"
    exit 1
fi

# 检查后端服务器配置
if [ -z "$BACKEND_SERVER" ] || [ "$BACKEND_SERVER" == "http://127.0.0.1:8001" ]; then
    echo "[WARN] BACKEND_SERVER 未配置或为默认值"
    read -p "请输入后端服务器地址 (如 http://api.xxx.com): " BACKEND_SERVER
fi

cd "$PROJECT_DIR"

# 创建目录
mkdir -p /var/www/zentea-license/admin
mkdir -p /var/www/zentea-license/portal

# 构建管理后台
echo "[INFO] 构建管理后台..."
cd "$PROJECT_DIR/frontend-admin"

docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
    npm config set registry https://registry.npmmirror.com
    npm install
    npm run build
"

rm -rf /var/www/zentea-license/admin/*
cp -r dist/* /var/www/zentea-license/admin/

# 构建用户门户
echo "[INFO] 构建用户门户..."
cd "$PROJECT_DIR/frontend-portal"

docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
    npm config set registry https://registry.npmmirror.com
    npm install
    npm run build
"

rm -rf /var/www/zentea-license/portal/*
cp -r dist/* /var/www/zentea-license/portal/

# 配置 Nginx
echo "[INFO] 配置 Nginx..."

# 管理后台
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
        proxy_pass ${BACKEND_SERVER};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 用户门户
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
        proxy_pass ${BACKEND_SERVER};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 测试并重载
nginx -t
systemctl reload nginx

echo ""
echo "=========================================="
echo "  前端部署完成！"
echo "=========================================="
echo ""
echo "管理后台: http://${DOMAIN_ADMIN}"
echo "用户门户: http://${DOMAIN_PORTAL}"
echo ""
echo "API 代理指向: ${BACKEND_SERVER}"
echo ""
echo "运行 ./setup-ssl.sh 配置 HTTPS"
echo ""

