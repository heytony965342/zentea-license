"""
促销活动 API 端点
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.response import success, error
from app.models.promo import PromoCampaign

router = APIRouter()


@router.get("/current")
async def get_current_promo(
    session: AsyncSession = Depends(get_session),
):
    """获取当前有效的促销活动"""
    now = datetime.utcnow()
    
    result = await session.execute(
        select(PromoCampaign).where(
            PromoCampaign.is_active == True,
            PromoCampaign.start_date <= now,
            PromoCampaign.end_date >= now,
        )
    )
    promos = result.scalars().all()
    
    # 过滤已达上限的活动
    valid_promos = []
    for p in promos:
        if p.max_uses is None or p.current_uses < p.max_uses:
            valid_promos.append({
                "id": p.id,
                "name": p.name,
                "code": p.code,
                "description": p.description,
                "end_date": p.end_date.isoformat() if p.end_date else None,
            })
    
    return success(valid_promos)


@router.post("/check")
async def check_promo_code(
    data: dict,
    session: AsyncSession = Depends(get_session),
):
    """检查促销码是否有效"""
    code = data.get("code")
    
    if not code:
        return error("请输入促销码")
    
    now = datetime.utcnow()
    
    result = await session.execute(
        select(PromoCampaign).where(
            PromoCampaign.code == code,
            PromoCampaign.is_active == True,
        )
    )
    promo = result.scalar_one_or_none()
    
    if not promo:
        return error("促销码无效", code=404)
    
    if promo.start_date and promo.start_date > now:
        return error("活动尚未开始")
    
    if promo.end_date and promo.end_date < now:
        return error("活动已结束")
    
    if promo.max_uses and promo.current_uses >= promo.max_uses:
        return error("活动名额已满")
    
    return success({
        "id": promo.id,
        "name": promo.name,
        "description": promo.description,
    }, "促销码有效")
