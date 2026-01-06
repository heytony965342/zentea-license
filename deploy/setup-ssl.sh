#!/bin/bash
# ============================================
# SSL 证书配置脚本
# 使用 Let's Encrypt 免费证书
# ============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=========================================="
echo "  SSL 证书配置"
echo "=========================================="

# 加载配置
if [ -f "$SCRIPT_DIR/.env" ]; then
    source "$SCRIPT_DIR/.env"
else
    echo "[ERROR] 请先复制 env.example 为 .env 并配置"
    exit 1
fi

# 检查配置
if [ -z "$SSL_EMAIL" ] || [ "$SSL_EMAIL" == "your-email@example.com" ]; then
    echo "[ERROR] 请在 .env 中配置 SSL_EMAIL"
    exit 1
fi

# 申请证书
apply_ssl() {
    local domain=$1
    
    echo "[INFO] 为 ${domain} 申请 SSL 证书..."
    
    certbot --nginx -d "$domain" \
        --non-interactive \
        --agree-tos \
        --email "$SSL_EMAIL" \
        --redirect
    
    echo "[INFO] ${domain} 证书申请完成"
}

# 配置自动续期
setup_auto_renew() {
    echo "[INFO] 配置证书自动续期..."
    
    # 添加定时任务
    (crontab -l 2>/dev/null | grep -v certbot; echo "0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
    
    echo "[INFO] 自动续期配置完成（每天凌晨3点检查）"
}

# 主函数
main() {
    echo ""
    echo "将为以下域名申请 SSL 证书："
    echo "  - ${DOMAIN_API}"
    echo "  - ${DOMAIN_ADMIN}"
    echo "  - ${DOMAIN_PORTAL}"
    echo ""
    echo "请确保域名已正确解析到本服务器！"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消"
        exit 0
    fi
    
    # 申请证书
    apply_ssl "$DOMAIN_API"
    apply_ssl "$DOMAIN_ADMIN"
    apply_ssl "$DOMAIN_PORTAL"
    
    # 配置自动续期
    setup_auto_renew
    
    echo ""
    echo "=========================================="
    echo "  SSL 配置完成！"
    echo "=========================================="
    echo ""
    echo "HTTPS 服务地址："
    echo "  API: https://${DOMAIN_API}"
    echo "  管理后台: https://${DOMAIN_ADMIN}"
    echo "  用户门户: https://${DOMAIN_PORTAL}"
    echo ""
    echo "证书将在到期前自动续期"
    echo ""
}

main

