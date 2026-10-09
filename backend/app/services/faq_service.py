from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.faq import FAQ
from app.schemas.faq import FAQCreate, FAQUpdate


def create_faq(db: Session, workspace_id: int, faq_data: FAQCreate) -> FAQ:
    new_faq = FAQ(
        workspace_id=workspace_id,
        question=faq_data.question,
        answer=faq_data.answer,
        question_bn=faq_data.question_bn,
        answer_bn=faq_data.answer_bn,
        question_en=faq_data.question_en,
        answer_en=faq_data.answer_en,
        language=faq_data.language,
        status="published",
    )
    db.add(new_faq)
    db.commit()
    db.refresh(new_faq)
    return new_faq


def get_faqs_by_workspace(db: Session, workspace_id: int) -> List[FAQ]:
    return (
        db.query(FAQ)
        .filter(FAQ.workspace_id == workspace_id)
        .order_by(FAQ.created_at.desc())
        .all()
    )


def get_faq_by_id(db: Session, faq_id: int) -> Optional[FAQ]:
    return db.query(FAQ).filter(FAQ.id == faq_id).first()


def update_faq(db: Session, faq: FAQ, faq_data: FAQUpdate) -> FAQ:
    update_data = faq_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(faq, key, value)
    db.commit()
    db.refresh(faq)
    return faq


def delete_faq(db: Session, faq: FAQ) -> None:
    db.delete(faq)
    db.commit()