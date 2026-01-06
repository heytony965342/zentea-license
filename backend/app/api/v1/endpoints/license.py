"""
授权验证 API 端点（供 ZenTea ERP 调用）
"""
import hashlib
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.database import get_session
from app.core.response import success, error
from app.models.license import License, LicenseHeartbeat
from app.models.user import User

router = APIRouter()


def generate_machine_id(info: dict) -> str:
    """根据机器信息生成机器码"""
    # 组合关键硬件信息
    raw = f"{info.get('cpu_id', '')}-{info.get('disk_serial', '')}-{info.get('mac_address', '')}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


@router.post("/activate")
async def activate_license(
    data: dict,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    激活授权
    
    请求参数:
    - license_key: 授权码
    - machine_info: 机器信息（CPU ID、硬盘序列号、MAC 地址等）
    - machine_id: 客户端生成的机器码（优先使用）
    """
    license_key = data.get("license_key")
    machine_info = data.get("machine_info", {})
    # 优先使用客户端传来的 machine_id，保证激活和验证一致
    machine_id = data.get("machine_id") or generate_machine_id(machine_info)
    
    if not license_key:
        return error("请提供授权码")
    
    # 查询授权
    result = await session.execute(
        select(License).where(License.license_key == license_key)
    )
    license = result.scalar_one_or_none()
    
    if not license:
        return error("授权码无效", code=404)
    
    if license.status == "revoked":
        return error("授权已被吊销", code=403)
    
    if license.status == "expired":
        return error("授权已过期", code=403)
    
    # 检查是否已绑定其他机器
    if license.machine_id and license.machine_id != machine_id:
        return error("授权已绑定其他设备，请联系管理员解绑", code=403)
    
    # 激活
    license.status = "active"
    license.machine_id = machine_id
    license.activated_at = datetime.utcnow()
    license.last_heartbeat = datetime.utcnow()
    
    await session.commit()
    
    return success({
        "license_key": license.license_key,
        "plan_type": license.plan_type,
        "expire_date": license.expire_date.isoformat() if license.expire_date else None,
        "max_users": license.max_users,
        "machine_id": machine_id,
    }, "激活成功")


@router.post("/verify")
async def verify_license(
    data: dict,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """
    验证授权（心跳）
    
    请求参数:
    - license_key: 授权码
    - machine_id: 机器码
    """
    license_key = data.get("license_key")
    machine_id = data.get("machine_id")
    
    if not license_key or not machine_id:
        return error("参数不完整")
    
    # 查询授权
    result = await session.execute(
        select(License).where(License.license_key == license_key)
    )
    license = result.scalar_one_or_none()
    
    if not license:
        return error("授权码无效", code=404)
    
    # 验证机器码
    if license.machine_id != machine_id:
        return error("机器码不匹配", code=403)
    
    # 检查状态
    if license.status == "revoked":
        return error("授权已被吊销", code=403)
    
    # 检查过期
    if license.expire_date and license.expire_date < datetime.utcnow():
        license.status = "expired"
        await session.commit()
        return error("授权已过期", code=403)
    
    # 更新心跳
    license.last_heartbeat = datetime.utcnow()
    
    # 记录心跳日志
    heartbeat = LicenseHeartbeat(
        license_id=license.id,
        machine_id=machine_id,
        ip_address=request.client.host if request.client else "unknown",
    )
    session.add(heartbeat)
    
    await session.commit()
    
    # 计算剩余天数
    remaining_days = None
    if license.expire_date:
        delta = license.expire_date - datetime.utcnow()
        remaining_days = max(0, delta.days)
    
    return success({
        "valid": True,
        "plan_type": license.plan_type,
        "expire_date": license.expire_date.isoformat() if license.expire_date else None,
        "remaining_days": remaining_days,
        "max_users": license.max_users,
    })


@router.post("/deactivate")
async def deactivate_license(
    data: dict,
    session: AsyncSession = Depends(get_session),
):
    """
    停用授权（用户主动解绑）
    
    请求参数:
    - license_key: 授权码
    - machine_id: 机器码
    """
    license_key = data.get("license_key")
    machine_id = data.get("machine_id")
    
    if not license_key or not machine_id:
        return error("参数不完整")
    
    # 查询授权
    result = await session.execute(
        select(License).where(License.license_key == license_key)
    )
    license = result.scalar_one_or_none()
    
    if not license:
        return error("授权码无效", code=404)
    
    # 验证机器码
    if license.machine_id != machine_id:
        return error("机器码不匹配", code=403)
    
    # 解绑
    license.machine_id = None
    license.status = "pending"
    
    await session.commit()
    
    return success(None, "已停用，可在其他设备重新激活")
