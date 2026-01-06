# ZenTea License 本地开发环境部署指南

> 适用于 Windows 11 + Docker Desktop

## 前置条件

1. **Python 3.11+** - [下载地址](https://www.python.org/downloads/)
2. **Node.js 20+** - [下载地址](https://nodejs.org/)
3. **PostgreSQL 15+** 或 **Docker Desktop** - [Docker 下载](https://www.docker.com/products/docker-desktop/)
4. **Git** - [下载地址](https://git-scm.com/)

---

# 方案一：无 Docker 本地开发（推荐）

适用于 Docker 网络有问题或者需要快速启动的场景。

## 1. 启动 PostgreSQL（使用 Docker 单独启动数据库）

```powershell
# 仅启动数据库容器
docker run -d --name zentea-license-db `
  -e POSTGRES_USER=license_admin `
  -e POSTGRES_PASSWORD=license_dev_pwd `
  -e POSTGRES_DB=zentea_license `
  -p 5433:5432 `
  postgres:15-alpine
```

## 2. 启动后端

```powershell
cd C:\Users\Linda\Documents\noo\zentea-license\backend

# 创建虚拟环境（首次）
python -m venv venv
.\venv\Scripts\Activate.ps1

# 安装依赖（首次）
pip install -r requirements.txt

# 设置环境变量
$env:DATABASE_URL = "postgresql+asyncpg://license_admin:license_dev_pwd@localhost:5433/zentea_license"
$env:SECRET_KEY = "dev-secret-key-for-testing"

# 启动后端
python run.py
```

后端启动后访问：http://localhost:8001/docs

## 3. 启动管理后台（新开 PowerShell 窗口）

```powershell
cd C:\Users\Linda\Documents\noo\zentea-license\frontend-admin

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

管理后台访问：http://localhost:3001

## 4. 启动用户门户（新开 PowerShell 窗口）

```powershell
cd C:\Users\Linda\Documents\noo\zentea-license\frontend-portal

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

用户门户访问：http://localhost:3002

## 5. 默认账号

- **管理员**：`admin` / `admin123`

---

# 方案二：Docker Compose 全容器部署

## 配置 Docker Desktop 镜像加速

由于国内网络问题，需要配置镜像加速：

1. 打开 Docker Desktop
2. 点击右上角 ⚙️ Settings
3. 选择 **Docker Engine**
4. 在 JSON 配置中添加：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerhub.icu",
    "https://docker.chenby.cn"
  ]
}
```

5. 点击 **Apply & Restart**

## 二、启动后端服务

### 方式一：使用 Docker Compose（推荐）

```powershell
# 进入项目目录
cd C:\Users\Linda\Documents\noo\zentea-license

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f
```

### 方式二：分步启动

```powershell
# 1. 启动 PostgreSQL
docker run -d --name zentea-license-db `
  -e POSTGRES_USER=license_admin `
  -e POSTGRES_PASSWORD=license_dev_pwd `
  -e POSTGRES_DB=zentea_license `
  -p 5433:5432 `
  postgres:15-alpine

# 2. 等待数据库就绪（约10秒）
Start-Sleep -Seconds 10

# 3. 启动后端
cd backend
pip install -r requirements.txt
$env:DATABASE_URL="postgresql+asyncpg://license_admin:license_dev_pwd@localhost:5433/zentea_license"
$env:SECRET_KEY="dev-secret-key-for-testing"
python run.py
```

### 验证后端启动

- API 文档：http://localhost:8001/docs
- 健康检查：http://localhost:8001/health
- 默认管理员：`admin` / `admin123`

## 三、启动前端服务

### 管理后台

```powershell
cd C:\Users\Linda\Documents\noo\zentea-license\frontend-admin

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

访问：http://localhost:3001

### 用户门户

```powershell
cd C:\Users\Linda\Documents\noo\zentea-license\frontend-portal

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

访问：http://localhost:3002

## 四、一键启动脚本

创建 `start-dev.ps1`：

```powershell
# 保存为 zentea-license/start-dev.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ZenTea License 本地开发环境启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查 Docker
$docker = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if (-not $docker) {
    Write-Host "[INFO] 正在启动 Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Write-Host "[INFO] 等待 Docker 启动（30秒）..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# 启动后端服务
Write-Host "[INFO] 启动后端服务..." -ForegroundColor Green
Set-Location $PSScriptRoot
docker compose up -d

# 等待后端就绪
Write-Host "[INFO] 等待后端就绪..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# 检查后端健康
$health = Invoke-RestMethod -Uri "http://localhost:8001/health" -ErrorAction SilentlyContinue
if ($health.status -eq "ok") {
    Write-Host "[OK] 后端服务已就绪" -ForegroundColor Green
} else {
    Write-Host "[WARN] 后端服务可能未完全就绪，请稍后检查" -ForegroundColor Yellow
}

# 启动前端
Write-Host "[INFO] 启动管理后台..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend-admin'; npm install; npm run dev"

Write-Host "[INFO] 启动用户门户..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend-portal'; npm install; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  服务地址" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  API 文档:   http://localhost:8001/docs" -ForegroundColor White
Write-Host "  管理后台:   http://localhost:3001" -ForegroundColor White
Write-Host "  用户门户:   http://localhost:3002" -ForegroundColor White
Write-Host ""
Write-Host "  默认管理员: admin / admin123" -ForegroundColor Yellow
Write-Host ""
```

使用方法：

```powershell
# 右键 start-dev.ps1 -> 使用 PowerShell 运行
# 或在 PowerShell 中执行：
.\start-dev.ps1
```

## 五、停止服务

```powershell
# 停止所有服务
cd C:\Users\Linda\Documents\noo\zentea-license
docker compose down

# 完全清理（包括数据库数据）
docker compose down -v
```

## 六、常见问题

### 1. Docker 镜像拉取失败

**错误**：`failed to resolve source metadata`

**解决**：配置镜像加速（见第一节）

### 2. 端口被占用

**错误**：`port is already allocated`

**解决**：

```powershell
# 查看端口占用
netstat -ano | findstr :8001
netstat -ano | findstr :5433

# 结束占用进程（替换 PID）
taskkill /PID <PID> /F
```

### 3. 数据库连接失败

**错误**：`connection refused`

**解决**：

```powershell
# 检查容器状态
docker ps

# 查看数据库日志
docker logs zentea-license-db
```

### 4. 前端依赖安装慢

**解决**：配置 npm 镜像

```powershell
npm config set registry https://registry.npmmirror.com
```

### 5. PowerShell 执行策略限制

**错误**：`无法加载文件...因为在此系统上禁止运行脚本`

**解决**：

```powershell
# 以管理员身份运行 PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 七、开发调试

### 查看后端日志

```powershell
docker compose logs -f backend
```

### 进入数据库

```powershell
docker exec -it zentea-license-db psql -U license_admin -d zentea_license
```

### 常用 SQL

```sql
-- 查看用户
SELECT id, username, email, role FROM users;

-- 查看授权
SELECT id, license_key, status, plan_type FROM licenses;

-- 查看订单
SELECT id, order_no, status, amount FROM orders;
```

### 重置数据库

```powershell
docker compose down -v
docker compose up -d
```

## 八、VS Code 推荐配置

### 推荐扩展

- Docker
- Python
- Vue - Official
- ESLint
- Prettier

### launch.json（调试后端）

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--port", "8001"],
      "cwd": "${workspaceFolder}/backend",
      "env": {
        "DATABASE_URL": "postgresql+asyncpg://license_admin:license_dev_pwd@localhost:5433/zentea_license",
        "SECRET_KEY": "dev-secret-key"
      }
    }
  ]
}
```

## 九、服务端口汇总

| 服务 | 端口 | 说明 |
|------|------|------|
| PostgreSQL | 5433 | 数据库（映射自容器5432） |
| 后端 API | 8001 | FastAPI 服务 |
| 管理后台 | 3001 | Vue 开发服务器 |
| 用户门户 | 3002 | Vue 开发服务器 |


