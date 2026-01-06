"""
API 路由汇总
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, license, admin, promo, portal, order, setting, page

api_router = APIRouter()

# 认证
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 授权验证（供 ZenTea ERP 调用）
api_router.include_router(license.router, prefix="/license", tags=["授权验证"])

# 管理后台
api_router.include_router(admin.router, prefix="/admin", tags=["管理后台"])

# 促销活动
api_router.include_router(promo.router, prefix="/promo", tags=["促销活动"])

# 用户门户
api_router.include_router(portal.router, prefix="/portal", tags=["用户门户"])

# 订单管理
api_router.include_router(order.router, prefix="/orders", tags=["订单管理"])

# 系统设置
api_router.include_router(setting.router, prefix="/settings", tags=["系统设置"])

# 页面内容管理
api_router.include_router(page.router, prefix="/pages", tags=["页面管理"])
