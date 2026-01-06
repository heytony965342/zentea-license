"""
ZenTea License Server - 授权验证服务
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
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
            admin = User(
                username="admin",
                email="admin@zentea.local",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            print("✅ 默认管理员已创建: admin / admin123")


app = FastAPI(
    title="ZenTea License Server",
    description="茗管家 ERP 软件授权验证服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "zentea-license"}
