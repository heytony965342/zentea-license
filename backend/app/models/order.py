"""
订单模型（用于记录客户购买授权的订单）
"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Order(SQLModel, table=True):
    """订单表"""
    __tablename__ = "orders"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # 订单号
    order_no: str = Field(max_length=50, unique=True, index=True)
    
    # 套餐类型
    plan_type: str = Field(max_length=20)
    
    # 金额
    amount: float = Field(default=0)
    
    # 状态：pending（待支付）, paid（已支付）, cancelled（已取消）, refunded（已退款）
    status: str = Field(default="pending", max_length=20, index=True)
    
    # 支付方式：manual（手动审核）, alipay（支付宝）, wechat（微信）
    payment_method: Optional[str] = Field(default=None, max_length=20)
    
    # 支付时间
    paid_at: Optional[datetime] = Field(default=None)
    
    # 关联的授权ID（支付成功后生成）
    license_id: Optional[int] = Field(default=None, foreign_key="licenses.id")
    
    # 促销码
    promo_code: Optional[str] = Field(default=None, max_length=50)
    
    # 备注（管理员审核时可填写）
    notes: Optional[str] = Field(default=None, max_length=500)
    
    # 支付凭证（客户上传）
    payment_proof: Optional[str] = Field(default=None, max_length=500)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
