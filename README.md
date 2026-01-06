# ZenTea License Server

茗管家 ERP 软件授权验证服务

## 项目结构

```
zentea-license/
├── backend/                # 授权服务后端
│   ├── app/
│   │   ├── api/           # API 端点
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   └── main.py        # 应用入口
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
├── frontend-admin/         # 管理后台前端（供您管理客户和授权）
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   └── views/         # 页面组件
│   ├── Dockerfile
│   └── package.json
├── frontend-portal/        # 用户门户前端（供客户注册、购买、查看授权）
│   ├── src/
│   │   ├── api/           # API 调用
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   └── views/         # 页面组件
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml      # Docker 编排
```

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker compose up -d

# 查看日志
docker compose logs -f
```

服务地址：
- 管理后台：http://localhost:3001 （您的管理界面）
- 用户门户：http://localhost:3002 （客户自助服务界面）
- API 文档：http://localhost:8001/docs
- 健康检查：http://localhost:8001/health

默认管理员账号：`admin` / `admin123`

### 本地开发

**后端**
```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（创建 .env 文件）
DATABASE_URL=postgresql+asyncpg://license_admin:password@localhost:5433/zentea_license
SECRET_KEY=your-secret-key

# 启动服务
python run.py
```

**前端**
```bash
cd frontend-admin

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## API 端点

### 授权验证（供 ZenTea ERP 调用）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/license/activate` | 激活授权 |
| POST | `/api/v1/license/verify` | 验证授权（心跳） |
| POST | `/api/v1/license/deactivate` | 停用授权 |

### 管理后台

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/admin/dashboard` | 仪表盘统计 |
| GET | `/api/v1/admin/customers` | 客户列表 |
| GET | `/api/v1/admin/licenses` | 授权列表 |
| POST | `/api/v1/admin/licenses` | 创建授权 |
| POST | `/api/v1/admin/licenses/{id}/extend` | 续期授权 |
| POST | `/api/v1/admin/licenses/{id}/revoke` | 吊销授权 |
| POST | `/api/v1/admin/licenses/{id}/unbind` | 解绑机器 |

### 促销活动

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/promo/current` | 当前有效活动 |
| POST | `/api/v1/promo/check` | 检查促销码 |

## 授权类型

| 类型 | 说明 |
|------|------|
| `monthly` | 月度版 |
| `yearly` | 年度版 |
| `lifetime` | 终身版 |
| `trial` | 试用版（7天） |
| `promo_free` | 限免版（活动） |
| `free_forever` | 永久免费 |

## 安全说明

1. 生产环境请务必修改 `SECRET_KEY`
2. 数据库密码请使用强密码
3. 建议启用 HTTPS
4. 建议配置防火墙，仅开放必要端口
