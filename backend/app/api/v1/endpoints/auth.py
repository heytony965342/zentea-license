"""
认证 API 端点
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.response import success, error
from app.core.login_limiter import login_limiter
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


def get_client_ip(request: Request) -> str:
    """获取客户端真实 IP"""
    # 优先从代理头获取
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """用户登录（带防暴力破解）"""
    client_ip = get_client_ip(request)
    username = form_data.username
    
    # 检查是否被锁定
    is_locked, remaining_seconds = login_limiter.is_locked(client_ip, username)
    if is_locked:
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        return error(
            f"登录尝试次数过多，请在 {minutes} 分 {seconds} 秒后重试",
            code=429
        )
    
    # 查询用户
    result = await session.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    # 验证失败
    if not user or not verify_password(form_data.password, user.hashed_password):
        fail_count, locked, lock_seconds = login_limiter.record_failure(client_ip, username)
        remaining = settings.LOGIN_MAX_ATTEMPTS - fail_count
        
        if locked:
            minutes = lock_seconds // 60
            return error(
                f"登录失败次数过多，账户已锁定 {minutes} 分钟",
                code=429
            )
        
        return error(
            f"用户名或密码错误，还剩 {remaining} 次尝试机会",
            code=401
        )
    
    if not user.is_active:
        return error("账户已被禁用", code=403)
    
    # 登录成功，清除失败记录
    login_limiter.record_success(client_ip, username)
    
    # 生成 Token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return success({
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "company_name": user.company_name,
        }
    })


@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息"""
    return success({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "company_name": current_user.company_name,
        "contact_name": current_user.contact_name,
        "phone": current_user.phone,
    })
