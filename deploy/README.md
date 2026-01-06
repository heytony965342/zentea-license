# ZenTea License 部署指南

## 服务器规划

| 服务器 | 用途 | 推荐配置 |
|--------|------|----------|
| 服务器A | 后端API + 数据库 | 2核4G，CentOS/Ubuntu |
| 服务器B (可选) | 前端静态资源 | 1核2G 或使用 CDN |

## 域名规划

| 域名 | 用途 |
|------|------|
| `api.jinghuatea.com` | 后端 API |
| `sq.jinghuatea.com` | 用户门户 |
| `admin.jinghuatea.com` | 管理后台 |

## 快速部署

### 方案一：单服务器部署（推荐）

```bash
# 1. 上传代码到服务器
scp -r zentea-license root@your-server:/opt/

# 2. SSH 登录服务器
ssh root@your-server

# 3. 执行部署脚本
cd /opt/zentea-license/deploy
chmod +x *.sh
./install.sh
./deploy-all.sh
./setup-ssl.sh
```

### 方案二：前后端分离部署

**后端服务器：**
```bash
./deploy-backend.sh
```

**前端服务器：**
```bash
./deploy-frontend.sh
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `install.sh` | 安装 Docker、Nginx 等依赖 |
| `deploy-all.sh` | 单服务器全量部署 |
| `deploy-backend.sh` | 仅部署后端 |
| `deploy-frontend.sh` | 仅部署前端 |
| `setup-ssl.sh` | 申请并配置 SSL 证书 |
| `nginx/` | Nginx 配置模板 |
| `env.example` | 环境变量模板 |

