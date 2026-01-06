"""
促销活动模型
"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class PromoCampaign(SQLModel, table=True):
    """促销活动表"""
    __tablename__ = "promo_campaigns"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 活动信息
    name: str = Field(max_length=100)
    code: str = Field(max_length=50, unique=True, index=True, description="活动码")
    description: Optional[str] = Field(default=None, max_length=500)
    
    # 时间范围
    start_date: datetime
    end_date: datetime
    
    # 状态
    is_active: bool = Field(default=True)
    
    # 限制
    max_uses: Optional[int] = Field(default=None, description="最大使用次数，null 表示不限")
    current_uses: int = Field(default=0)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
