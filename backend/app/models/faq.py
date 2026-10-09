from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func

from app.core.database import Base


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    question_bn = Column(Text, nullable=True)
    answer_bn = Column(Text, nullable=True)
    question_en = Column(Text, nullable=True)
    answer_en = Column(Text, nullable=True)
    language = Column(String(10), default="bn", nullable=False)
    status = Column(String(20), default="published", nullable=False)  # draft, published, archived
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<FAQ(id={self.id}, workspace_id={self.workspace_id})>"