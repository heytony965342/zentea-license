"""
认证 API 端点
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.core.response import success, error
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """用户登录"""
    # 查询用户
    result = await session.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        return error("用户名或密码错误", code=401)
    
    if not user.is_active:
        return error("账户已被禁用", code=403)
    
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
