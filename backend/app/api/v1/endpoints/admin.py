"""
管理后台 API 端点
"""
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from sqlmodel import select, func

from app.core.database import get_session
from app.core.response import success, error
from app.core.security import get_password_hash
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.license import License, LicenseHeartbeat
from app.models.order import Order
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
                "is_active": c.is_active,
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
        "is_active": customer.is_active,
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


@router.post("/customers")
async def create_customer(
    data: dict,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """创建客户"""
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not email:
        return error("请填写用户名和邮箱")

    # 唯一性校验
    exists_username = await session.execute(select(User).where(User.username == username))
    if exists_username.scalar_one_or_none():
        return error("用户名已被使用")

    exists_email = await session.execute(select(User).where(User.email == email))
    if exists_email.scalar_one_or_none():
        return error("邮箱已被注册")

    generated_password: Optional[str] = None
    if not password:
        # 不回显管理员输入的密码；若未填写则生成一次性初始密码供管理员抄录
        import uuid
        generated_password = f"ZT{uuid.uuid4().hex[:10]}"
        password = generated_password

    customer = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role="customer",
        is_active=bool(data.get("is_active", True)),
        company_name=data.get("company_name"),
        contact_name=data.get("contact_name"),
        phone=data.get("phone"),
        address=data.get("address"),
        created_at=datetime.utcnow(),
        updated_at=None,
    )
    session.add(customer)
    await session.commit()
    await session.refresh(customer)

    return success(
        {
            "id": customer.id,
            "initial_password": generated_password,  # 仅当自动生成时返回
        },
        "创建成功",
    )


@router.put("/customers/{customer_id}")
async def update_customer(
    customer_id: int,
    data: dict,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """编辑客户"""
    result = await session.execute(select(User).where(User.id == customer_id, User.role == "customer"))
    customer = result.scalar_one_or_none()
    if not customer:
        return error("客户不存在", code=404)

    # 用户名/邮箱变更需校验唯一性
    if "username" in data and data["username"] is not None:
        new_username = str(data["username"]).strip()
        if not new_username:
            return error("用户名不能为空")
        exists = await session.execute(select(User).where(User.username == new_username, User.id != customer_id))
        if exists.scalar_one_or_none():
            return error("用户名已被使用")
        customer.username = new_username

    if "email" in data and data["email"] is not None:
        new_email = str(data["email"]).strip()
        if not new_email:
            return error("邮箱不能为空")
        exists = await session.execute(select(User).where(User.email == new_email, User.id != customer_id))
        if exists.scalar_one_or_none():
            return error("邮箱已被注册")
        customer.email = new_email

    # 其他字段
    for key in ["company_name", "contact_name", "phone", "address"]:
        if key in data:
            setattr(customer, key, data.get(key))

    if "is_active" in data:
        customer.is_active = bool(data.get("is_active"))

    customer.updated_at = datetime.utcnow()
    session.add(customer)
    await session.commit()

    return success({"id": customer.id}, "更新成功")


@router.delete("/customers/{customer_id}")
async def delete_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """删除客户（会同时清理其授权/订单/心跳记录）"""
    result = await session.execute(select(User).where(User.id == customer_id, User.role == "customer"))
    customer = result.scalar_one_or_none()
    if not customer:
        return error("客户不存在", code=404)

    # 先清理关联数据，避免外键约束导致删除失败
    lic_ids_res = await session.execute(select(License.id).where(License.user_id == customer_id))
    license_ids = list(lic_ids_res.scalars().all())

    if license_ids:
        await session.execute(delete(LicenseHeartbeat).where(LicenseHeartbeat.license_id.in_(license_ids)))
        # 订单里可能引用 license_id，也可能仅按 user_id 关联，统一按 user_id 清理

    await session.execute(delete(Order).where(Order.user_id == customer_id))
    await session.execute(delete(License).where(License.user_id == customer_id))

    await session.delete(customer)
    await session.commit()

    return success(None, "删除成功")


# ==================== 管理员管理 ====================

@router.get("/admins")
async def get_admins(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """获取管理员列表"""
    offset = (page - 1) * page_size
    result = await session.execute(
        select(User)
        .where(User.role == "admin")
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    admins = result.scalars().all()

    total = await session.execute(select(func.count()).select_from(User).where(User.role == "admin"))
    total = total.scalar() or 0

    return success({
        "items": [
            {
                "id": a.id,
                "username": a.username,
                "email": a.email,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in admins
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("/admins")
async def create_admin(
    data: dict,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """创建管理员"""
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not username or not email or not password:
        return error("请填写用户名、邮箱和密码")

    exists_username = await session.execute(select(User).where(User.username == username))
    if exists_username.scalar_one_or_none():
        return error("用户名已被使用")

    exists_email = await session.execute(select(User).where(User.email == email))
    if exists_email.scalar_one_or_none():
        return error("邮箱已被注册")

    admin = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role="admin",
        is_active=bool(data.get("is_active", True)),
        created_at=datetime.utcnow(),
        updated_at=None,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)

    return success({"id": admin.id}, "创建成功")


@router.put("/admins/{admin_id}")
async def update_admin(
    admin_id: int,
    data: dict,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
):
    """编辑管理员"""
    result = await session.execute(select(User).where(User.id == admin_id, User.role == "admin"))
    admin = result.scalar_one_or_none()
    if not admin:
        return error("管理员不存在", code=404)

    if "username" in data and data["username"] is not None:
        new_username = str(data["username"]).strip()
        if not new_username:
            return error("用户名不能为空")
        exists = await session.execute(select(User).where(User.username == new_username, User.id != admin_id))
        if exists.scalar_one_or_none():
            return error("用户名已被使用")
        admin.username = new_username

    if "email" in data and data["email"] is not None:
        new_email = str(data["email"]).strip()
        if not new_email:
            return error("邮箱不能为空")
        exists = await session.execute(select(User).where(User.email == new_email, User.id != admin_id))
        if exists.scalar_one_or_none():
            return error("邮箱已被注册")
        admin.email = new_email

    if "is_active" in data:
        # 避免把自己禁用导致无法再管理
        if admin_id == current_admin.id and not bool(data.get("is_active")):
            return error("不能禁用当前登录管理员")
        admin.is_active = bool(data.get("is_active"))

    admin.updated_at = datetime.utcnow()
    session.add(admin)
    await session.commit()

    return success({"id": admin.id}, "更新成功")


@router.delete("/admins/{admin_id}")
async def delete_admin(
    admin_id: int,
    session: AsyncSession = Depends(get_session),
    current_admin: User = Depends(get_current_admin),
):
    """删除管理员"""
    if admin_id == current_admin.id:
        return error("不能删除当前登录管理员")

    # 至少保留一个管理员
    total_admins = await session.execute(select(func.count()).select_from(User).where(User.role == "admin"))
    total_admins = total_admins.scalar() or 0
    if total_admins <= 1:
        return error("至少需要保留一个管理员")

    result = await session.execute(select(User).where(User.id == admin_id, User.role == "admin"))
    admin = result.scalar_one_or_none()
    if not admin:
        return error("管理员不存在", code=404)

    await session.delete(admin)
    await session.commit()

    return success(None, "删除成功")


@router.post("/admins/{admin_id}/password")
async def set_admin_password(
    admin_id: int,
    data: dict,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """修改管理员密码（重置/改密）"""
    new_password = (data.get("new_password") or "").strip()
    if not new_password:
        return error("请填写新密码")
    if len(new_password) < 6:
        return error("密码至少 6 位")

    result = await session.execute(select(User).where(User.id == admin_id, User.role == "admin"))
    admin = result.scalar_one_or_none()
    if not admin:
        return error("管理员不存在", code=404)

    admin.hashed_password = get_password_hash(new_password)
    admin.updated_at = datetime.utcnow()
    session.add(admin)
    await session.commit()

    return success({"id": admin.id}, "密码已更新")

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
