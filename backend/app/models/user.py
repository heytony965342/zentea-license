"""
用户模型
"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """用户表"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    email: str = Field(max_length=100, unique=True, index=True)
    hashed_password: str = Field(max_length=255)
    
    # 角色：admin（管理员）, customer（客户）
    role: str = Field(default="customer", max_length=20)
    is_active: bool = Field(default=True)
    
    # 企业信息
    company_name: Optional[str] = Field(default=None, max_length=200)
    contact_name: Optional[str] = Field(default=None, max_length=50)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=500)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
