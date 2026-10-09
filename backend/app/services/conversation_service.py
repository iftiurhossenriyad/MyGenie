"""
Conversation Service — Manages conversations and messages.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate


def create_conversation(
    db: Session, owner_user_id: int, conversation_data: ConversationCreate
) -> Conversation:
    """Create a new conversation."""
    new_conversation = Conversation(
        workspace_id=conversation_data.workspace_id,
        owner_user_id=owner_user_id,
        customer_id=conversation_data.customer_id,
        channel=conversation_data.channel,
        status="active",
        language=conversation_data.language,
    )
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    return new_conversation


def get_conversations_by_workspace(
    db: Session, workspace_id: int
) -> List[Conversation]:
    """List all conversations in a workspace."""
    return (
        db.query(Conversation)
        .filter(Conversation.workspace_id == workspace_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


def get_conversations_for_owner(
    db: Session, owner_user_id: int
) -> List[Conversation]:
    """List conversations owned by a user (personal use)."""
    return (
        db.query(Conversation)
        .filter(Conversation.owner_user_id == owner_user_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


def get_conversation_by_id(
    db: Session, conversation_id: int
) -> Optional[Conversation]:
    """Get a conversation by ID."""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_messages(
    db: Session, conversation_id: int, limit: int = 100
) -> List[Message]:
    """Get messages in a conversation."""
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .all()
    )


def add_message(
    db: Session,
    conversation_id: int,
    sender_type: str,
    content: str,
    sender_id: Optional[int] = None,
    content_type: str = "text",
) -> Message:
    """Add a message to a conversation."""
    new_message = Message(
        conversation_id=conversation_id,
        sender_type=sender_type,
        sender_id=sender_id,
        content=content,
        content_type=content_type,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def update_conversation(
    db: Session, conversation: Conversation, conversation_data: ConversationUpdate
) -> Conversation:
    """Update a conversation (status, staff assignment, language)."""
    update_data = conversation_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(conversation, key, value)
    db.commit()
    db.refresh(conversation)
    return conversation


def set_handoff(
    db: Session, conversation: Conversation, staff_user_id: int
) -> Conversation:
    """Mark a conversation as handoff to human staff."""
    conversation.status = "handoff"
    conversation.assigned_staff_id = staff_user_id
    db.commit()
    db.refresh(conversation)
    return conversation


def close_conversation(db: Session, conversation: Conversation) -> Conversation:
    """Close a conversation."""
    conversation.status = "closed"
    db.commit()
    db.refresh(conversation)
    return conversation