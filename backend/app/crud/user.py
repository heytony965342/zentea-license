"""
用户 CRUD 操作
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserCreate, UserRole
from app.core.security import get_password_hash, verify_password


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    role: Optional[UserRole] = None,
) -> List[User]:
    """获取用户列表"""
    query = select(User)
    if role:
        query = query.where(User.role == role)
    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_user(session: AsyncSession, user_in: UserCreate, role: UserRole = UserRole.CUSTOMER) -> User:
    """创建用户"""
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        phone=user_in.phone,
        company_name=user_in.company_name,
        contact_name=user_in.contact_name,
        role=role,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    """验证用户"""
    # 支持用户名或邮箱登录
    user = await get_user_by_username(session, username)
    if not user:
        user = await get_user_by_email(session, username)
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    session.add(user)
    await session.commit()
    
    return user


async def update_user_password(session: AsyncSession, user: User, new_password: str) -> User:
    """更新用户密码"""
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_admin_if_not_exists(session: AsyncSession, username: str, password: str, email: str) -> Optional[User]:
    """创建管理员（如果不存在）"""
    existing = await get_user_by_username(session, username)
    if existing:
        return None
    
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role=UserRole.ADMIN,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

