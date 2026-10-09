from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    name_bn = Column(String(200), nullable=True)
    name_en = Column(String(200), nullable=True)
    description_bn = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    sku = Column(String(100), nullable=True, index=True)
    price = Column(Numeric(12, 2), nullable=False, default=0)
    currency = Column(String(10), default="BDT", nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    image_url = Column(String(500), nullable=True)
    language = Column(String(10), default="bn", nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, inactive, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, sku={self.sku})>"