"""
页面内容管理 API
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.response import success, error
from app.api.deps import get_current_admin
from app.models.user import User
from app.models.page import Page, DEFAULT_PAGES

router = APIRouter()


async def init_default_pages(session: AsyncSession):
    """初始化默认页面"""
    for item in DEFAULT_PAGES:
        result = await session.execute(
            select(Page).where(Page.slug == item["slug"])
        )
        if not result.scalar_one_or_none():
            page = Page(**item)
            session.add(page)
    await session.commit()


@router.get("")
async def get_pages(
    status: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """获取所有页面列表（管理员）"""
    await init_default_pages(session)
    
    query = select(Page)
    if status:
        query = query.where(Page.status == status)
    query = query.order_by(Page.sort_order, Page.id)
    
    result = await session.execute(query)
    pages = result.scalars().all()
    
    data = []
    for p in pages:
        data.append({
            "id": p.id,
            "slug": p.slug,
            "title": p.title,
            "subtitle": p.subtitle,
            "status": p.status,
            "sort_order": p.sort_order,
            "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        })
    
    return success(data)


@router.get("/{page_id}")
async def get_page(
    page_id: int,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """获取页面详情（管理员）"""
    result = await session.execute(
        select(Page).where(Page.id == page_id)
    )
    page = result.scalar_one_or_none()
    
    if not page:
        return error("页面不存在")
    
    return success({
        "id": page.id,
        "slug": page.slug,
        "title": page.title,
        "subtitle": page.subtitle,
        "content": page.content,
        "meta_description": page.meta_description,
        "status": page.status,
        "sort_order": page.sort_order,
        "created_at": page.created_at.isoformat() if page.created_at else None,
        "updated_at": page.updated_at.isoformat() if page.updated_at else None,
    })


@router.put("/{page_id}")
async def update_page(
    page_id: int,
    data: dict,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """更新页面（管理员）"""
    result = await session.execute(
        select(Page).where(Page.id == page_id)
    )
    page = result.scalar_one_or_none()
    
    if not page:
        return error("页面不存在")
    
    # 更新字段
    if "title" in data:
        page.title = data["title"]
    if "subtitle" in data:
        page.subtitle = data["subtitle"]
    if "content" in data:
        page.content = data["content"]
    if "meta_description" in data:
        page.meta_description = data["meta_description"]
    if "status" in data:
        page.status = data["status"]
    if "sort_order" in data:
        page.sort_order = data["sort_order"]
    
    page.updated_at = datetime.utcnow()
    
    await session.commit()
    
    return success({"id": page.id}, "页面更新成功")


@router.post("")
async def create_page(
    data: dict,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """创建新页面（管理员）"""
    slug = data.get("slug")
    if not slug:
        return error("请提供页面标识（slug）")
    
    # 检查 slug 是否已存在
    result = await session.execute(
        select(Page).where(Page.slug == slug)
    )
    if result.scalar_one_or_none():
        return error(f"页面标识 '{slug}' 已存在")
    
    page = Page(
        slug=slug,
        title=data.get("title", "新页面"),
        subtitle=data.get("subtitle"),
        content=data.get("content", ""),
        meta_description=data.get("meta_description"),
        status=data.get("status", "draft"),
        sort_order=data.get("sort_order", 0),
    )
    
    session.add(page)
    await session.commit()
    await session.refresh(page)
    
    return success({"id": page.id}, "页面创建成功")


@router.delete("/{page_id}")
async def delete_page(
    page_id: int,
    session: AsyncSession = Depends(get_session),
    admin: User = Depends(get_current_admin),
):
    """删除页面（管理员）"""
    result = await session.execute(
        select(Page).where(Page.id == page_id)
    )
    page = result.scalar_one_or_none()
    
    if not page:
        return error("页面不存在")
    
    await session.delete(page)
    await session.commit()
    
    return success(None, "页面删除成功")


# ========== 公开 API（无需登录） ==========

@router.get("/public/menu")
async def get_public_page_menu(
    session: AsyncSession = Depends(get_session),
):
    """获取公开页面菜单列表（无需登录）"""
    await init_default_pages(session)
    
    result = await session.execute(
        select(Page)
        .where(Page.status == "published")
        .order_by(Page.sort_order)
    )
    pages = result.scalars().all()
    
    data = []
    for p in pages:
        data.append({
            "slug": p.slug,
            "title": p.title,
        })
    
    return success(data)


@router.get("/public/{slug}")
async def get_public_page(
    slug: str,
    session: AsyncSession = Depends(get_session),
):
    """获取公开页面内容（无需登录）"""
    await init_default_pages(session)
    
    result = await session.execute(
        select(Page).where(Page.slug == slug, Page.status == "published")
    )
    page = result.scalar_one_or_none()
    
    if not page:
        raise HTTPException(status_code=404, detail="页面不存在")
    
    return success({
        "slug": page.slug,
        "title": page.title,
        "subtitle": page.subtitle,
        "content": page.content,
        "meta_description": page.meta_description,
    })

