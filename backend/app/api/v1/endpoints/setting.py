"""
系统设置 API 端点
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.response import success, error
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.setting import SystemSetting, DEFAULT_SETTINGS, SettingKeys

router = APIRouter()


async def init_default_settings(session: AsyncSession):
    """初始化默认设置"""
    for item in DEFAULT_SETTINGS:
        result = await session.execute(
            select(SystemSetting).where(SystemSetting.key == item["key"])
        )
        if not result.scalar_one_or_none():
            setting = SystemSetting(**item)
            session.add(setting)
    await session.commit()


@router.get("")
async def get_settings(
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """获取系统设置列表"""
    # 确保默认设置已初始化
    await init_default_settings(session)
    
    query = select(SystemSetting)
    if category:
        query = query.where(SystemSetting.category == category)
    query = query.order_by(SystemSetting.category, SystemSetting.key)
    
    result = await session.execute(query)
    settings = result.scalars().all()
    
    # 敏感字段脱敏
    data = []
    sensitive_keys = [
        SettingKeys.ALIPAY_PRIVATE_KEY,
        SettingKeys.ALIPAY_PUBLIC_KEY,
        SettingKeys.WECHAT_API_KEY,
    ]
    for s in settings:
        item = {
            "id": s.id,
            "key": s.key,
            "value": "******" if s.key in sensitive_keys and s.value else s.value,
            "description": s.description,
            "category": s.category,
            "has_value": bool(s.value),  # 标记是否已配置
        }
        data.append(item)
    
    return success(data)


@router.put("")
async def update_settings(
    data: dict,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """批量更新设置"""
    settings = data.get("settings", {})
    if not settings:
        return error("请提供要更新的设置")
    
    updated = []
    for key, value in settings.items():
        # 跳过脱敏占位符
        if value == "******":
            continue
            
        result = await session.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = str(value) if value is not None else ""
            setting.updated_at = datetime.utcnow()
            updated.append(key)
        else:
            # 创建新设置
            new_setting = SystemSetting(
                key=key,
                value=str(value) if value is not None else "",
                category="custom",
            )
            session.add(new_setting)
            updated.append(key)
    
    await session.commit()
    return success({"updated": updated}, f"已更新 {len(updated)} 项设置")


@router.get("/payment")
async def get_payment_settings(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """获取支付设置"""
    await init_default_settings(session)
    
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.category == "payment")
    )
    settings = result.scalars().all()
    
    # 转换为字典格式
    data = {}
    for s in settings:
        # 敏感字段脱敏
        if s.key in [SettingKeys.ALIPAY_PRIVATE_KEY, SettingKeys.ALIPAY_PUBLIC_KEY, SettingKeys.WECHAT_API_KEY]:
            data[s.key] = "******" if s.value else ""
            data[f"{s.key}_configured"] = bool(s.value)
        else:
            data[s.key] = s.value
    
    return success(data)


@router.get("/contact")
async def get_contact_settings(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """获取客服联系方式设置"""
    await init_default_settings(session)
    
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.category == "contact")
    )
    settings = result.scalars().all()
    
    data = {s.key: s.value for s in settings}
    return success(data)


@router.get("/public/contact")
async def get_public_contact(
    session: AsyncSession = Depends(get_session),
):
    """获取公开的客服联系方式（无需登录）"""
    await init_default_settings(session)
    
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.category == "contact")
    )
    settings = result.scalars().all()
    
    data = {s.key: s.value for s in settings}
    return success(data)


@router.get("/public/homepage")
async def get_public_homepage(
    session: AsyncSession = Depends(get_session),
):
    """获取公开的首页配置（无需登录）"""
    await init_default_settings(session)
    
    # 获取首页相关配置
    categories = ["homepage", "particles"]
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.category.in_(categories))
    )
    settings = result.scalars().all()
    
    data = {s.key: s.value for s in settings}
    
    # 解析 JSON 字段
    import json
    json_keys = [
        SettingKeys.AI_DEMO_QUERIES,
        SettingKeys.FEATURES_LIST,
        SettingKeys.TESTIMONIALS_LIST,
        SettingKeys.FOOTER_LINKS,
    ]
    for key in json_keys:
        if key in data:
            try:
                data[key] = json.loads(data[key])
            except:
                data[key] = []
    
    # 数值类型转换
    numeric_keys = [
        SettingKeys.PARTICLE_COUNT,
        SettingKeys.PARTICLE_GROWTH_SPEED,
        SettingKeys.PARTICLE_INTERACTION,
    ]
    for key in numeric_keys:
        if key in data:
            try:
                data[key] = float(data[key])
            except:
                pass
    
    return success(data)


@router.get("/homepage")
async def get_homepage_settings(
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """获取首页配置（管理员）"""
    await init_default_settings(session)
    
    categories = ["homepage", "particles"]
    result = await session.execute(
        select(SystemSetting).where(SystemSetting.category.in_(categories))
    )
    settings = result.scalars().all()
    
    data = []
    for s in settings:
        data.append({
            "id": s.id,
            "key": s.key,
            "value": s.value,
            "description": s.description,
            "category": s.category,
        })
    
    return success(data)

