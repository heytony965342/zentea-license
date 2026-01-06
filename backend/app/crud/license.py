"""
授权许可证 CRUD 操作
"""

from typing import Optional, List
from datetime import datetime, date, timedelta
import secrets
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.models.license import (
    License, LicenseCreate, LicenseStatus, PlanType,
    HeartbeatLog
)
from app.core.security import generate_license_key


async def get_license_by_id(session: AsyncSession, license_id: int) -> Optional[License]:
    """根据ID获取授权"""
    result = await session.execute(select(License).where(License.id == license_id))
    return result.scalar_one_or_none()


async def get_license_by_key(session: AsyncSession, license_key: str) -> Optional[License]:
    """根据授权码获取授权"""
    result = await session.execute(select(License).where(License.license_key == license_key))
    return result.scalar_one_or_none()


async def get_licenses(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    status: Optional[LicenseStatus] = None,
) -> List[License]:
    """获取授权列表"""
    query = select(License)
    if user_id:
        query = query.where(License.user_id == user_id)
    if status:
        query = query.where(License.status == status)
    query = query.order_by(License.created_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_licenses_count(
    session: AsyncSession,
    user_id: Optional[int] = None,
    status: Optional[LicenseStatus] = None,
) -> int:
    """获取授权数量"""
    query = select(func.count(License.id))
    if user_id:
        query = query.where(License.user_id == user_id)
    if status:
        query = query.where(License.status == status)
    result = await session.execute(query)
    return result.scalar_one()


async def create_license(session: AsyncSession, license_in: LicenseCreate) -> License:
    """创建授权"""
    # 计算到期时间
    expire_date = license_in.expire_date
    if not expire_date and license_in.plan_type in [PlanType.MONTHLY, PlanType.YEARLY, PlanType.TRIAL]:
        today = date.today()
        if license_in.plan_type == PlanType.MONTHLY:
            expire_date = today + timedelta(days=30)
        elif license_in.plan_type == PlanType.YEARLY:
            expire_date = today + timedelta(days=365)
        elif license_in.plan_type == PlanType.TRIAL:
            expire_date = today + timedelta(days=7)
    
    license = License(
        license_key=generate_license_key(),
        user_id=license_in.user_id,
        plan_type=license_in.plan_type,
        expire_date=expire_date,
        max_users=license_in.max_users,
        notes=license_in.notes,
        status=LicenseStatus.PENDING,
    )
    session.add(license)
    await session.commit()
    await session.refresh(license)
    return license


async def activate_license(
    session: AsyncSession,
    license: License,
    machine_id: str,
) -> License:
    """激活授权"""
    license.status = LicenseStatus.ACTIVE
    license.machine_id = machine_id
    license.activated_at = datetime.utcnow()
    license.start_date = date.today()
    license.current_token = secrets.token_urlsafe(32)
    license.updated_at = datetime.utcnow()
    
    session.add(license)
    await session.commit()
    await session.refresh(license)
    return license


async def update_heartbeat(
    session: AsyncSession,
    license: License,
    ip_address: Optional[str] = None,
    app_version: Optional[str] = None,
) -> str:
    """更新心跳，返回新令牌"""
    new_token = secrets.token_urlsafe(32)
    
    license.current_token = new_token
    license.last_heartbeat = datetime.utcnow()
    license.heartbeat_count += 1
    license.updated_at = datetime.utcnow()
    
    # 记录心跳日志
    log = HeartbeatLog(
        license_id=license.id,
        machine_id=license.machine_id or "",
        ip_address=ip_address,
        app_version=app_version,
    )
    session.add(log)
    session.add(license)
    await session.commit()
    
    return new_token


async def revoke_license(session: AsyncSession, license: License, reason: str = "") -> License:
    """吊销授权"""
    license.status = LicenseStatus.REVOKED
    license.notes = f"{license.notes or ''}\n[吊销] {reason}".strip()
    license.updated_at = datetime.utcnow()
    
    session.add(license)
    await session.commit()
    await session.refresh(license)
    return license


async def deactivate_license(session: AsyncSession, license: License) -> License:
    """解绑授权（换机器）"""
    license.machine_id = None
    license.activated_at = None
    license.current_token = None
    license.status = LicenseStatus.PENDING
    license.updated_at = datetime.utcnow()
    
    session.add(license)
    await session.commit()
    await session.refresh(license)
    return license


async def extend_license(session: AsyncSession, license: License, days: int) -> License:
    """延长授权有效期"""
    if license.expire_date:
        # 如果已过期，从今天开始计算
        base_date = max(license.expire_date, date.today())
        license.expire_date = base_date + timedelta(days=days)
    else:
        license.expire_date = date.today() + timedelta(days=days)
    
    # 如果之前过期了，重新激活
    if license.status == LicenseStatus.EXPIRED:
        license.status = LicenseStatus.ACTIVE
    
    license.updated_at = datetime.utcnow()
    session.add(license)
    await session.commit()
    await session.refresh(license)
    return license


def check_license_validity(license: License) -> tuple[bool, str]:
    """
    检查授权有效性
    返回 (是否有效, 原因)
    """
    # 状态检查
    if license.status == LicenseStatus.REVOKED:
        return False, "授权已被吊销"
    if license.status == LicenseStatus.SUSPENDED:
        return False, "授权已被暂停"
    if license.status == LicenseStatus.PENDING:
        return False, "授权尚未激活"
    
    # 到期检查（永久授权和免费永久除外）
    if license.plan_type not in [PlanType.LIFETIME, PlanType.FREE_FOREVER]:
        if license.expire_date and license.expire_date < date.today():
            return False, "授权已过期"
    
    return True, "有效"

