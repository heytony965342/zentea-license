"""
订单管理 API 端点
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
import uuid

from app.core.database import get_session
from app.core.response import success, error
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.models.order import Order
from app.models.license import License
from app.models.promo import PromoCampaign

router = APIRouter()

# 套餐价格
PLAN_PRICES = {
    "trial": 0,
    "monthly": 99,
    "yearly": 899,
    "lifetime": 2999,
}

# 套餐对应的有效期（天）
PLAN_DURATIONS = {
    "trial": 7,
    "monthly": 30,
    "yearly": 365,
    "lifetime": None,  # 永久
}

# 套餐对应的用户数
PLAN_MAX_USERS = {
    "trial": 2,
    "monthly": 5,
    "yearly": 10,
    "lifetime": 999,
}


@router.post("/create")
async def create_order(
    data: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    创建订单
    
    客户选择套餐后创建订单，等待支付
    """
    plan_type = data.get("plan_type")
    promo_code = data.get("promo_code")
    
    if plan_type not in PLAN_PRICES:
        return error("无效的套餐类型")
    
    # 试用版检查
    if plan_type == "trial":
        result = await session.execute(
            select(License).where(
                License.user_id == current_user.id,
                License.plan_type == "trial"
            )
        )
        if result.scalar_one_or_none():
            return error("您已使用过试用版")
    
    # 计算金额
    amount = PLAN_PRICES[plan_type]
    
    # 检查促销码
    if promo_code:
        promo_result = await session.execute(
            select(PromoCampaign).where(
                PromoCampaign.code == promo_code,
                PromoCampaign.is_active == True,
            )
        )
        promo = promo_result.scalar_one_or_none()
        
        if promo:
            now = datetime.utcnow()
            if promo.start_date <= now <= promo.end_date:
                if promo.max_uses is None or promo.current_uses < promo.max_uses:
                    # 限免活动 - 金额归零
                    amount = 0
    
    # 生成订单号
    order_no = f"ORD{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
    
    # 创建订单
    order = Order(
        user_id=current_user.id,
        order_no=order_no,
        plan_type=plan_type,
        amount=amount,
        status="pending",
        promo_code=promo_code,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    
    # 免费订单自动完成
    if amount == 0:
        return await complete_order_internal(session, order, current_user)
    
    return success({
        "order_id": order.id,
        "order_no": order.order_no,
        "amount": amount,
        "plan_type": plan_type,
        "payment_info": {
            "method": "manual",
            "instructions": "请转账后上传支付凭证，我们将在1-2个工作日内审核",
            # TODO: 添加收款账户信息
        }
    })


@router.post("/{order_id}/upload-proof")
async def upload_payment_proof(
    order_id: int,
    proof_url: str,  # 简化版：前端上传后传URL
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """上传支付凭证"""
    result = await session.execute(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error("订单不存在")
    
    if order.status != "pending":
        return error("订单状态不允许此操作")
    
    order.payment_proof = proof_url
    order.notes = f"{order.notes or ''}\n[{datetime.utcnow().isoformat()}] 客户上传支付凭证".strip()
    await session.commit()
    
    return success(None, "上传成功，请等待审核")


@router.get("/my")
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """获取我的订单列表"""
    result = await session.execute(
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    
    return success([
        {
            "id": o.id,
            "order_no": o.order_no,
            "plan_type": o.plan_type,
            "amount": o.amount,
            "status": o.status,
            "payment_method": o.payment_method,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "paid_at": o.paid_at.isoformat() if o.paid_at else None,
        }
        for o in orders
    ])


# ==================== 管理员接口 ====================

@router.get("/admin/list")
async def admin_get_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_admin),
):
    """管理员：获取订单列表"""
    offset = (page - 1) * page_size
    
    query = select(Order)
    count_query = select(func.count()).select_from(Order)
    
    if status:
        query = query.where(Order.status == status)
        count_query = count_query.where(Order.status == status)
    
    result = await session.execute(
        query.order_by(Order.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    orders = result.scalars().all()
    
    total = await session.execute(count_query)
    total = total.scalar() or 0
    
    # 获取用户信息
    user_ids = list(set(o.user_id for o in orders))
    users_result = await session.execute(
        select(User).where(User.id.in_(user_ids))
    )
    users_map = {u.id: u for u in users_result.scalars().all()}
    
    return success({
        "items": [
            {
                "id": o.id,
                "order_no": o.order_no,
                "user_id": o.user_id,
                "user": {
                    "username": users_map[o.user_id].username,
                    "company_name": users_map[o.user_id].company_name,
                } if o.user_id in users_map else None,
                "plan_type": o.plan_type,
                "amount": o.amount,
                "status": o.status,
                "payment_proof": o.payment_proof,
                "promo_code": o.promo_code,
                "notes": o.notes,
                "created_at": o.created_at.isoformat() if o.created_at else None,
                "paid_at": o.paid_at.isoformat() if o.paid_at else None,
            }
            for o in orders
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("/admin/{order_id}/approve")
async def admin_approve_order(
    order_id: int,
    notes: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """管理员：审核通过订单"""
    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error("订单不存在")
    
    if order.status != "pending":
        return error("订单状态不允许此操作")
    
    # 获取订单用户
    user_result = await session.execute(
        select(User).where(User.id == order.user_id)
    )
    user = user_result.scalar_one_or_none()
    
    if not user:
        return error("订单用户不存在")
    
    return await complete_order_internal(session, order, user, notes, admin.username)


@router.post("/admin/{order_id}/reject")
async def admin_reject_order(
    order_id: int,
    reason: str,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """管理员：拒绝订单"""
    result = await session.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()
    
    if not order:
        return error("订单不存在")
    
    if order.status != "pending":
        return error("订单状态不允许此操作")
    
    order.status = "cancelled"
    order.notes = f"{order.notes or ''}\n[{datetime.utcnow().isoformat()}] 管理员 {admin.username} 拒绝: {reason}".strip()
    await session.commit()
    
    return success(None, "已拒绝")


async def complete_order_internal(
    session: AsyncSession,
    order: Order,
    user: User,
    notes: Optional[str] = None,
    admin_username: Optional[str] = None,
):
    """内部函数：完成订单并生成授权"""
    # 计算到期日期
    duration = PLAN_DURATIONS.get(order.plan_type)
    expire_date = None
    if duration:
        expire_date = datetime.utcnow() + timedelta(days=duration)
    
    # 生成授权码
    license_key = f"ZT-{order.plan_type.upper()[:3]}-{uuid.uuid4().hex[:16].upper()}"
    
    # 创建授权
    license = License(
        user_id=user.id,
        license_key=license_key,
        plan_type=order.plan_type,
        status="pending",
        expire_date=expire_date,
        max_users=PLAN_MAX_USERS.get(order.plan_type, 5),
    )
    session.add(license)
    await session.flush()
    
    # 更新订单
    order.status = "paid"
    order.paid_at = datetime.utcnow()
    order.license_id = license.id
    order.payment_method = "manual"
    
    if notes:
        order.notes = f"{order.notes or ''}\n[{datetime.utcnow().isoformat()}] {notes}".strip()
    if admin_username:
        order.notes = f"{order.notes or ''}\n[{datetime.utcnow().isoformat()}] 管理员 {admin_username} 审核通过".strip()
    
    # 更新促销码使用次数
    if order.promo_code:
        promo_result = await session.execute(
            select(PromoCampaign).where(PromoCampaign.code == order.promo_code)
        )
        promo = promo_result.scalar_one_or_none()
        if promo:
            promo.current_uses += 1
    
    await session.commit()
    
    return success({
        "license_key": license_key,
        "plan_type": order.plan_type,
        "expire_date": expire_date.isoformat() if expire_date else None,
        "max_users": license.max_users,
    }, "订单完成，授权已生成")

