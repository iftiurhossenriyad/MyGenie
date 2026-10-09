from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class OrderItemBase(BaseModel):
    product_id: Optional[int] = None
    product_name_snapshot: str
    unit_price_snapshot: Decimal = Field(..., ge=0)
    quantity: int = Field(..., gt=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int
    line_total: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    customer_id: Optional[int] = None
    delivery_details: Optional[str] = None
    customer_notes: Optional[str] = None
    currency: str = Field(default="BDT", max_length=10)
    delivery_fee: Decimal = Field(default=Decimal("0"), ge=0)


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    delivery_details: Optional[str] = None
    customer_notes: Optional[str] = None
    delivery_fee: Optional[Decimal] = Field(None, ge=0)


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(requested|validated|confirmed|preparing|dispatched|completed|cancelled)$")


class OrderResponse(OrderBase):
    id: int
    workspace_id: int
    order_number: str
    status: str
    subtotal: Decimal
    total: Decimal
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)