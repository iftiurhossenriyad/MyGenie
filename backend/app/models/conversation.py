from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    channel = Column(String(30), default="web", nullable=False)  # web, whatsapp, messenger, email, sms
    status = Column(String(20), default="active", nullable=False)  # active, handoff, closed
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    language = Column(String(10), default="bn", nullable=False)  # bn, en, auto
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, workspace_id={self.workspace_id}, status={self.status})>"