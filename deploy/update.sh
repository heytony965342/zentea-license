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
fi

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
        echo "[INFO] 更新后端..."
        docker compose -f docker-compose.prod.yml build backend
        docker compose -f docker-compose.prod.yml up -d backend
        echo "[INFO] 后端更新完成"
        ;;
    2)
        echo "[INFO] 更新前端..."
        
        # 管理后台
        cd "$PROJECT_DIR/frontend-admin"
        docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
            npm config set registry https://registry.npmmirror.com
            npm install
            npm run build
        "
        rm -rf /var/www/zentea-license/admin/*
        cp -r dist/* /var/www/zentea-license/admin/
        
        # 用户门户
        cd "$PROJECT_DIR/frontend-portal"
        docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
            npm config set registry https://registry.npmmirror.com
            npm install
            npm run build
        "
        rm -rf /var/www/zentea-license/portal/*
        cp -r dist/* /var/www/zentea-license/portal/
        
        echo "[INFO] 前端更新完成"
        ;;
    3)
        echo "[INFO] 更新全部..."
        
        # 后端
        docker compose -f docker-compose.prod.yml build backend
        docker compose -f docker-compose.prod.yml up -d backend
        
        # 前端
        cd "$PROJECT_DIR/frontend-admin"
        docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
            npm config set registry https://registry.npmmirror.com
            npm install
            npm run build
        "
        rm -rf /var/www/zentea-license/admin/*
        cp -r dist/* /var/www/zentea-license/admin/
        
        cd "$PROJECT_DIR/frontend-portal"
        docker run --rm -v "$(pwd)":/app -w /app node:20-alpine sh -c "
            npm config set registry https://registry.npmmirror.com
            npm install
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

