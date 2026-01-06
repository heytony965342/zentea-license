"""
管理后台 API 端点
"""
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

from app.core.database import get_session
from app.core.response import success, error
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.license import License
from app.models.promo import PromoCampaign

router = APIRouter()


# ==================== 仪表盘 ====================

@router.get("/dashboard")
async def get_dashboard(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """获取仪表盘统计"""
    # 客户总数
    total_customers = await session.execute(
        select(func.count()).select_from(User).where(User.role == "customer")
    )
    total_customers = total_customers.scalar() or 0
    
    # 授权统计
    now = datetime.utcnow()
    seven_days_later = now + timedelta(days=7)
    
    # 有效授权
    active_count = await session.execute(
        select(func.count()).select_from(License).where(License.status == "active")
    )
    active_count = active_count.scalar() or 0
    
    # 待激活
    pending_count = await session.execute(
        select(func.count()).select_from(License).where(License.status == "pending")
    )
    pending_count = pending_count.scalar() or 0
    
    # 已过期
    expired_count = await session.execute(
        select(func.count()).select_from(License).where(License.status == "expired")
    )
    expired_count = expired_count.scalar() or 0
    
    # 即将到期（7天内）
    expiring_soon = await session.execute(
        select(func.count()).select_from(License).where(
            License.status == "active",
            License.expire_date != None,
            License.expire_date <= seven_days_later,
            License.expire_date > now,
        )
    )
    expiring_soon = expiring_soon.scalar() or 0
    
    return success({
        "total_customers": total_customers,
        "licenses": {
            "active": active_count,
            "pending": pending_count,
            "expired": expired_count,
            "expiring_soon": expiring_soon,
        }
    })


# ==================== 客户管理 ====================

@router.get("/customers")
async def get_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """获取客户列表"""
    offset = (page - 1) * page_size
    
    # 查询客户
    result = await session.execute(
        select(User)
        .where(User.role == "customer")
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    customers = result.scalars().all()
    
    # 总数
    total = await session.execute(
        select(func.count()).select_from(User).where(User.role == "customer")
    )
    total = total.scalar() or 0
    
    return success({
        "items": [
            {
                "id": c.id,
                "username": c.username,
                "email": c.email,
                "company_name": c.company_name,
                "contact_name": c.contact_name,
                "phone": c.phone,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in customers
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/customers/{customer_id}")
async def get_customer_detail(
    customer_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """获取客户详情"""
    result = await session.execute(
        select(User).where(User.id == customer_id, User.role == "customer")
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(status_code=404, detail="客户不存在")
    
    # 获取授权记录
    licenses_result = await session.execute(
        select(License)
        .where(License.user_id == customer_id)
        .order_by(License.created_at.desc())
    )
    licenses = licenses_result.scalars().all()
    
    return success({
        "id": customer.id,
        "username": customer.username,
        "email": customer.email,
        "company_name": customer.company_name,
        "contact_name": customer.contact_name,
        "phone": customer.phone,
        "address": customer.address,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
        "licenses": [
            {
                "id": lic.id,
                "license_key": lic.license_key,
                "plan_type": lic.plan_type,
                "status": lic.status,
                "created_at": lic.created_at.isoformat() if lic.created_at else None,
                "expire_date": lic.expire_date.isoformat() if lic.expire_date else None,
            }
            for lic in licenses
        ],
    })


# ==================== 授权管理 ====================

@router.get("/licenses")
async def get_licenses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    user_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """获取授权列表"""
    offset = (page - 1) * page_size
    
    # 构建查询
    query = select(License)
    count_query = select(func.count()).select_from(License)
    
    if status:
        query = query.where(License.status == status)
        count_query = count_query.where(License.status == status)
    
    if user_id:
        query = query.where(License.user_id == user_id)
        count_query = count_query.where(License.user_id == user_id)
    
    # 执行查询
    result = await session.execute(
        query.order_by(License.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    licenses = result.scalars().all()
    
    # 总数
    total = await session.execute(count_query)
    total = total.scalar() or 0
    
    # 获取用户信息
    user_ids = list(set(lic.user_id for lic in licenses))
    users_result = await session.execute(
        select(User).where(User.id.in_(user_ids))
    )
    users_map = {u.id: u for u in users_result.scalars().all()}
    
    return success({
        "items": [
            {
                "id": lic.id,
                "user_id": lic.user_id,
                "license_key": lic.license_key,
                "plan_type": lic.plan_type,
                "status": lic.status,
                "created_at": lic.created_at.isoformat() if lic.created_at else None,
                "activated_at": lic.activated_at.isoformat() if lic.activated_at else None,
                "expire_date": lic.expire_date.isoformat() if lic.expire_date else None,
                "machine_id": lic.machine_id,
                "max_users": lic.max_users,
                "notes": lic.notes,
                "user": {
                    "username": users_map[lic.user_id].username,
                    "company_name": users_map[lic.user_id].company_name,
                } if lic.user_id in users_map else None,
            }
            for lic in licenses
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("/licenses")
async def create_license(
    data: dict,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """创建授权"""
    import uuid
    
    user_id = int(data.get("user_id"))  # 确保是整数
    plan_type = data.get("plan_type", "yearly")
    expire_date_str = data.get("expire_date")
    max_users = data.get("max_users", 5)
    notes = data.get("notes")
    
    # 验证用户存在
    user_result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        return error("用户不存在")
    
    # 计算到期日期
    expire_date = None
    if expire_date_str:
        expire_date = datetime.fromisoformat(expire_date_str)
    elif plan_type == "monthly":
        expire_date = datetime.utcnow() + timedelta(days=30)
    elif plan_type == "yearly":
        expire_date = datetime.utcnow() + timedelta(days=365)
    elif plan_type == "trial":
        expire_date = datetime.utcnow() + timedelta(days=7)
    # lifetime, promo_free, free_forever 无到期日期
    
    # 生成授权码
    license_key = f"ZT-{plan_type.upper()[:3]}-{uuid.uuid4().hex[:16].upper()}"
    
    # 创建授权
    license = License(
        user_id=user_id,
        license_key=license_key,
        plan_type=plan_type,
        status="pending",
        expire_date=expire_date,
        max_users=max_users,
        notes=notes,
    )
    session.add(license)
    await session.commit()
    await session.refresh(license)
    
    return success({
        "id": license.id,
        "license_key": license.license_key,
        "expire_date": license.expire_date.isoformat() if license.expire_date else None,
    }, "创建成功")


@router.post("/licenses/{license_id}/extend")
async def extend_license(
    license_id: int,
    days: int = Query(..., ge=1),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """续期授权"""
    result = await session.execute(
        select(License).where(License.id == license_id)
    )
    license = result.scalar_one_or_none()
    
    if not license:
        return error("授权不存在")
    
    # 计算新到期日期
    base_date = license.expire_date or datetime.utcnow()
    if base_date < datetime.utcnow():
        base_date = datetime.utcnow()
    
    license.expire_date = base_date + timedelta(days=days)
    
    # 如果已过期，重新激活
    if license.status == "expired":
        license.status = "active"
    
    await session.commit()
    
    return success({
        "new_expire_date": license.expire_date.isoformat()
    }, "续期成功")


@router.post("/licenses/{license_id}/revoke")
async def revoke_license(
    license_id: int,
    reason: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """吊销授权"""
    result = await session.execute(
        select(License).where(License.id == license_id)
    )
    license = result.scalar_one_or_none()
    
    if not license:
        return error("授权不存在")
    
    license.status = "revoked"
    if reason:
        license.notes = f"{license.notes or ''}\n[吊销原因] {reason}".strip()
    
    await session.commit()
    
    return success(None, "已吊销")


@router.post("/licenses/{license_id}/unbind")
async def unbind_license(
    license_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """解绑机器"""
    result = await session.execute(
        select(License).where(License.id == license_id)
    )
    license = result.scalar_one_or_none()
    
    if not license:
        return error("授权不存在")
    
    license.machine_id = None
    await session.commit()
    
    return success(None, "已解绑")


# ==================== 促销活动管理 ====================

@router.get("/promos")
async def get_promos(
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """获取促销活动列表"""
    result = await session.execute(
        select(PromoCampaign).order_by(PromoCampaign.created_at.desc())
    )
    promos = result.scalars().all()
    
    return success([
        {
            "id": p.id,
            "name": p.name,
            "code": p.code,
            "description": p.description,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "end_date": p.end_date.isoformat() if p.end_date else None,
            "is_active": p.is_active,
            "max_uses": p.max_uses,
            "current_uses": p.current_uses,
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in promos
    ])


@router.post("/promos")
async def create_promo(
    data: dict,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """创建促销活动"""
    promo = PromoCampaign(
        name=data.get("name"),
        code=data.get("code"),
        description=data.get("description"),
        start_date=datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None,
        end_date=datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None,
        max_uses=data.get("max_uses"),
        is_active=True,
    )
    session.add(promo)
    await session.commit()
    await session.refresh(promo)
    
    return success({"id": promo.id}, "创建成功")
