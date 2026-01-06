"""
授权模型
"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class License(SQLModel, table=True):
    """授权表"""
    __tablename__ = "licenses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # 授权码（唯一）
    license_key: str = Field(max_length=100, unique=True, index=True)
    
    # 版本类型
    # monthly: 月度版, yearly: 年度版, lifetime: 终身版
    # trial: 试用版, promo_free: 限免版, free_forever: 永久免费
    plan_type: str = Field(default="yearly", max_length=20)
    
    # 状态：pending（待激活）, active（已激活）, expired（已过期）, revoked（已吊销）
    status: str = Field(default="pending", max_length=20, index=True)
    
    # 机器绑定
    machine_id: Optional[str] = Field(default=None, max_length=64, index=True)
    
    # 时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    activated_at: Optional[datetime] = Field(default=None)
    expire_date: Optional[datetime] = Field(default=None, index=True)
    last_heartbeat: Optional[datetime] = Field(default=None)
    
    # 限制
    max_users: int = Field(default=5, description="最大用户数")
    
    # 备注
    notes: Optional[str] = Field(default=None, max_length=1000)


class LicenseHeartbeat(SQLModel, table=True):
    """授权心跳记录表"""
    __tablename__ = "license_heartbeats"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    license_id: int = Field(foreign_key="licenses.id", index=True)
    machine_id: str = Field(max_length=64)
    ip_address: str = Field(max_length=45)
    created_at: datetime = Field(default_factory=datetime.utcnow)
