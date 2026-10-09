from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from decimal import Decimal


class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    name_bn: Optional[str] = None
    name_en: Optional[str] = None
    description_bn: Optional[str] = None
    description_en: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=100)
    price: Decimal = Field(..., ge=0)
    currency: str = Field(default="BDT", max_length=10)
    stock_quantity: int = Field(default=0, ge=0)
    is_available: bool = True
    image_url: Optional[str] = None
    language: str = Field(default="bn", pattern="^(bn|en)$")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    name_bn: Optional[str] = None
    name_en: Optional[str] = None
    description_bn: Optional[str] = None
    description_en: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[Decimal] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|archived)$")


class ProductResponse(ProductBase):
    id: int
    workspace_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class InventoryAdjustment(BaseModel):
    quantity_change: int