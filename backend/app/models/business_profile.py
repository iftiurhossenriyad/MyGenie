from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.core.database import Base


class BusinessProfile(Base):
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), unique=True, nullable=False, index=True)
    business_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    opening_hours = Column(Text, nullable=True)  # JSON string later
    delivery_info = Column(Text, nullable=True)
    policies = Column(Text, nullable=True)
    default_language = Column(String(10), default="bn", nullable=False)
    supported_languages = Column(String(50), default="bn,en", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<BusinessProfile(workspace_id={self.workspace_id}, name={self.business_name})>"