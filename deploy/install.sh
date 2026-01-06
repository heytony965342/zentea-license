#!/bin/bash
# ============================================
# 服务器环境初始化脚本
# 支持 CentOS 7/8 和 Ubuntu 18/20/22
# ============================================

set -e

echo "=========================================="
echo "  ZenTea License 服务器环境初始化"
echo "=========================================="

# 检测系统类型
if [ -f /etc/redhat-release ]; then
    OS="centos"
    echo "[INFO] 检测到 CentOS/RHEL 系统"
elif [ -f /etc/lsb-release ]; then
    OS="ubuntu"
    echo "[INFO] 检测到 Ubuntu 系统"
else
    echo "[ERROR] 不支持的操作系统"
    exit 1
fi

# 安装 Docker
install_docker() {
    if command -v docker &> /dev/null; then
        echo "[INFO] Docker 已安装，跳过"
        return
    fi
    
    echo "[INFO] 正在安装 Docker..."
    
    if [ "$OS" == "centos" ]; then
        yum install -y yum-utils
        yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    else
        apt-get update
        apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
        curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    fi
    
    # 配置 Docker 镜像加速
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerhub.icu",
    "https://docker.chenby.cn"
  ]
}
EOF
    
    systemctl enable docker
    systemctl start docker
    
    echo "[INFO] Docker 安装完成"
}

# 安装 Nginx
install_nginx() {
    if command -v nginx &> /dev/null; then
        echo "[INFO] Nginx 已安装，跳过"
        return
    fi
    
    echo "[INFO] 正在安装 Nginx..."
    
    if [ "$OS" == "centos" ]; then
        yum install -y nginx
    else
        apt-get install -y nginx
    fi
    
    systemctl enable nginx
    systemctl start nginx
    
    echo "[INFO] Nginx 安装完成"
}

# 安装 Certbot (用于 SSL 证书)
install_certbot() {
    if command -v certbot &> /dev/null; then
        echo "[INFO] Certbot 已安装，跳过"
        return
    fi
    
    echo "[INFO] 正在安装 Certbot..."
    
    if [ "$OS" == "centos" ]; then
        yum install -y epel-release
        yum install -y certbot python3-certbot-nginx
    else
        apt-get install -y certbot python3-certbot-nginx
    fi
    
    echo "[INFO] Certbot 安装完成"
}

# 安装 Git
install_git() {
    if command -v git &> /dev/null; then
        echo "[INFO] Git 已安装，跳过"
        return
    fi
    
    echo "[INFO] 正在安装 Git..."
    
    if [ "$OS" == "centos" ]; then
        yum install -y git
    else
        apt-get install -y git
    fi
    
    echo "[INFO] Git 安装完成"
}

# 创建目录结构
create_directories() {
    echo "[INFO] 创建目录结构..."
    
    mkdir -p /opt/zentea-license
    mkdir -p /var/www/zentea-license/admin
    mkdir -p /var/www/zentea-license/portal
    mkdir -p /var/log/zentea-license
    
    echo "[INFO] 目录创建完成"
}

# 配置防火墙
configure_firewall() {
    echo "[INFO] 配置防火墙..."
    
    if [ "$OS" == "centos" ]; then
        if command -v firewall-cmd &> /dev/null; then
            firewall-cmd --permanent --add-service=http
            firewall-cmd --permanent --add-service=https
            firewall-cmd --permanent --add-port=8001/tcp
            firewall-cmd --reload
        fi
    else
        if command -v ufw &> /dev/null; then
            ufw allow 80/tcp
            ufw allow 443/tcp
            ufw allow 8001/tcp
        fi
    fi
    
    echo "[INFO] 防火墙配置完成"
}

# 执行安装
main() {
    install_docker
    install_nginx
    install_certbot
    install_git
    create_directories
    configure_firewall
    
    echo ""
    echo "=========================================="
    echo "  环境初始化完成！"
    echo "=========================================="
    echo ""
    echo "下一步："
    echo "1. 复制 env.example 为 .env 并修改配置"
    echo "2. 运行 ./deploy-all.sh 部署服务"
    echo "3. 运行 ./setup-ssl.sh 配置 SSL 证书"
    echo ""
}

main

