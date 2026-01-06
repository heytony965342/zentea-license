"""
用户门户 API 端点
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import uuid

from app.core.database import get_session
from app.core.security import get_password_hash
from app.core.response import success, error
from app.api.deps import get_current_user
from app.models.user import User
from app.models.license import License

router = APIRouter()


# ==================== 用户注册 ====================

@router.post("/register")
async def register(
    data: dict,
    session: AsyncSession = Depends(get_session),
):
    """用户注册"""
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    
    if not username or not email or not password:
        return error("请填写必填项")
    
    # 检查用户名是否已存在
    result = await session.execute(
        select(User).where(User.username == username)
    )
    if result.scalar_one_or_none():
        return error("用户名已被使用")
    
    # 检查邮箱是否已存在
    result = await session.execute(
        select(User).where(User.email == email)
    )
    if result.scalar_one_or_none():
        return error("邮箱已被注册")
    
    # 创建用户
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        role="customer",
        company_name=data.get("company_name"),
        contact_name=data.get("contact_name"),
        phone=data.get("phone"),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return success({"id": user.id}, "注册成功")


# ==================== 我的授权 ====================

@router.get("/licenses")
async def get_my_licenses(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """获取我的授权列表"""
    result = await session.execute(
        select(License)
        .where(License.user_id == current_user.id)
        .order_by(License.created_at.desc())
    )
    licenses = result.scalars().all()
    
    return success([
        {
            "id": lic.id,
            "license_key": lic.license_key,
            "plan_type": lic.plan_type,
            "status": lic.status,
            "created_at": lic.created_at.isoformat() if lic.created_at else None,
            "activated_at": lic.activated_at.isoformat() if lic.activated_at else None,
            "expire_date": lic.expire_date.isoformat() if lic.expire_date else None,
            "machine_id": lic.machine_id,
            "max_users": lic.max_users,
        }
        for lic in licenses
    ])


# ==================== 套餐信息 ====================

@router.get("/plans")
async def get_plans():
    """获取套餐列表"""
    plans = [
        {
            "type": "trial",
            "name": "试用版",
            "price": 0,
            "period": "7天",
            "max_users": 2,
            "features": ["全功能体验", "基础技术支持"],
        },
        {
            "type": "monthly",
            "name": "月度版",
            "price": 99,
            "period": "月",
            "max_users": 5,
            "features": ["全部功能", "邮件支持", "数据备份"],
        },
        {
            "type": "yearly",
            "name": "年度版",
            "price": 899,
            "period": "年",
            "max_users": 10,
            "features": ["全部功能", "优先支持", "数据备份", "免费升级"],
        },
        {
            "type": "lifetime",
            "name": "终身版",
            "price": 2999,
            "period": "永久",
            "max_users": 999,
            "features": ["全部功能", "专属支持", "永久更新", "优先新功能"],
        },
    ]
    return success(plans)


# ==================== 订单（简化版，实际需集成支付） ====================

@router.post("/orders")
async def create_order(
    data: dict,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """创建订单（简化版）"""
    plan_type = data.get("plan_type")
    promo_code = data.get("promo_code")
    
    # 价格映射
    price_map = {
        "trial": 0,
        "monthly": 99,
        "yearly": 899,
        "lifetime": 2999,
    }
    
    if plan_type not in price_map:
        return error("无效的套餐类型")
    
    amount = price_map[plan_type]
    
    # TODO: 检查促销码并应用折扣
    # TODO: 集成支付系统
    
    # 试用版直接生成授权
    if plan_type == "trial":
        # 检查是否已有试用记录
        result = await session.execute(
            select(License).where(
                License.user_id == current_user.id,
                License.plan_type == "trial"
            )
        )
        if result.scalar_one_or_none():
            return error("您已使用过试用版")
        
        # 生成授权
        license_key = f"ZT-TRL-{uuid.uuid4().hex[:16].upper()}"
        license = License(
            user_id=current_user.id,
            license_key=license_key,
            plan_type="trial",
            status="pending",
            expire_date=datetime.utcnow() + timedelta(days=7),
            max_users=2,
        )
        session.add(license)
        await session.commit()
        
        return success({
            "license_key": license_key,
            "message": "试用授权已生成，请在软件中激活"
        })
    
    # 付费版返回支付信息（简化版）
    order_no = f"ORD{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
    
    return success({
        "order_no": order_no,
        "amount": amount,
        "plan_type": plan_type,
        "message": "请联系客服完成支付",
        # TODO: 返回支付链接
    })


@router.get("/orders")
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """获取我的订单（简化版）"""
    # TODO: 实现订单表和查询
    return success([])

