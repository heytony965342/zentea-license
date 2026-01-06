#!/bin/bash
# ============================================
# 服务状态检查脚本
# ============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "  ZenTea License 服务状态"
echo "=========================================="

# 加载配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
fi

echo ""
echo "📦 Docker 容器状态："
echo "----------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep zentea-license || echo "  (无运行中的容器)"

echo ""
echo "🌐 Nginx 状态："
echo "----------------------------------------"
systemctl is-active nginx && echo "  Nginx 运行中" || echo "  Nginx 未运行"

echo ""
echo "🔒 SSL 证书状态："
echo "----------------------------------------"
for domain in "$DOMAIN_API" "$DOMAIN_ADMIN" "$DOMAIN_PORTAL"; do
    if [ -n "$domain" ]; then
        cert_file="/etc/letsencrypt/live/$domain/fullchain.pem"
        if [ -f "$cert_file" ]; then
            expiry=$(openssl x509 -enddate -noout -in "$cert_file" 2>/dev/null | cut -d= -f2)
            echo "  $domain: 有效期至 $expiry"
        else
            echo "  $domain: 未配置 SSL"
        fi
    fi
done

echo ""
echo "💾 磁盘空间："
echo "----------------------------------------"
df -h / | tail -1 | awk '{print "  已用: " $3 " / " $2 " (" $5 ")"}'

echo ""
echo "🔧 Docker 磁盘占用："
echo "----------------------------------------"
docker system df 2>/dev/null || echo "  (无法获取)"

echo ""
echo "📊 API 健康检查："
echo "----------------------------------------"
if [ -n "$DOMAIN_API" ]; then
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8001/health" 2>/dev/null)
    if [ "$status" == "200" ]; then
        echo "  ✅ API 正常 (HTTP $status)"
    else
        echo "  ❌ API 异常 (HTTP $status)"
    fi
else
    echo "  (未配置域名)"
fi

echo ""

