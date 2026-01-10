"""
ZenTea License Server - 授权验证服务
"""
from contextlib import asynccontextmanager
import secrets
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.core.config import settings
from app.api.v1.router import api_router
# 导入所有模型以确保表被创建
from app.models import user, license, order, promo, setting, page  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    # 创建默认管理员（如果不存在）
    await create_default_admin()
    yield


async def create_default_admin():
    """创建默认管理员账户"""
    from app.core.database import async_session
    from app.models.user import User
    from app.core.security import get_password_hash
    from sqlmodel import select
    
    async with async_session() as session:
        # 检查是否已存在管理员
        result = await session.execute(
            select(User).where(User.role == "admin")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            username = (settings.ADMIN_USERNAME or "admin").strip()
            email = (settings.ADMIN_EMAIL or "admin@zentea.local").strip()
            password = (settings.ADMIN_PASSWORD or "").strip()

            # 生产环境兜底：如果未显式配置密码或仍是弱默认值，则生成强随机密码（避免固定 admin123）
            # 管理员后续可在后台自行新增/删改管理员或修改密码。
            if settings.is_production and (not password or password == "admin123"):
                password = secrets.token_urlsafe(18)  # ~24 chars
                print("[SECURITY] 生产环境检测到未设置管理员强密码，已自动生成随机初始密码，请立即登录后台修改：")
                print(f"[SECURITY] ADMIN_USERNAME={username}")
                print(f"[SECURITY] ADMIN_PASSWORD={password}")

            admin = User(
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                role="admin",
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            if not settings.is_production:
                print(f"✅ 默认管理员已创建: {username} / {password}")


app = FastAPI(
    title="ZenTea License Server",
    description="茗管家 ERP 软件授权验证服务",
    version="1.0.0",
    # 生产环境建议关闭 docs/openapi（减少暴露面）
    openapi_url=None if settings.is_production else "/openapi.json",
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or [],
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "zentea-license"}
