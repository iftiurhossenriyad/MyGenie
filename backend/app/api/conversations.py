from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    HandoffRequest,
)
from app.schemas.message import MessageCreate, MessageResponse, ChatRequest, ChatResponse
from app.services import (
    conversation_service,
    ai_service,
    workspace_service,
)

router = APIRouter(prefix="/api/v1/conversations", tags=["Conversations"])


# ============ Create Conversation ============

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new conversation in a workspace."""
    member = workspace_service.get_member(
        db, conversation_data.workspace_id, current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return conversation_service.create_conversation(
        db, current_user.id, conversation_data
    )


# ============ List Conversations ============

@router.get("/workspaces/{workspace_id}", response_model=List[ConversationResponse])
def list_workspace_conversations(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all conversations in a workspace."""
    member = workspace_service.get_member(db, workspace_id, current_user.id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return conversation_service.get_conversations_by_workspace(db, workspace_id)


# ============ Get Conversation ============

@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a conversation by ID."""
    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    member = workspace_service.get_member(
        db, conversation.workspace_id, current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return conversation


# ============ Get Messages ============

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def list_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all messages in a conversation."""
    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    member = workspace_service.get_member(
        db, conversation.workspace_id, current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return conversation_service.get_messages(db, conversation_id)


# ============ Send Message + AI Response ============

@router.post(
    "/{conversation_id}/messages",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    conversation_id: int,
    chat_data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Send a user message and receive an AI response.
    If the conversation is in handoff mode, AI is paused.
    """
    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    member = workspace_service.get_member(
        db, conversation.workspace_id, current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    if conversation.status == "closed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conversation is closed",
        )

    # Save user message
    user_message = conversation_service.add_message(
        db,
        conversation_id,
        sender_type="user",
        content=chat_data.content,
        sender_id=current_user.id,
    )

    # If in handoff, do not generate AI response
    if conversation.status == "handoff":
        assistant_message = conversation_service.add_message(
            db,
            conversation_id,
            sender_type="system",
            content="Waiting for staff response. AI replies are paused.",
        )
        return ChatResponse(
            user_message=user_message,
            assistant_message=assistant_message,
            conversation_id=conversation_id,
        )

    # Generate AI response (grounded)
    ai_response_text = await ai_service.generate_ai_response(
        db, conversation, chat_data.content
    )

    assistant_message = conversation_service.add_message(
        db,
        conversation_id,
        sender_type="assistant",
        content=ai_response_text,
    )

    return ChatResponse(
        user_message=user_message,
        assistant_message=assistant_message,
        conversation_id=conversation_id,
    )


# ============ Human Handoff ============

@router.post("/{conversation_id}/handoff", response_model=ConversationResponse)
def handoff_conversation(
    conversation_id: int,
    handoff_data: HandoffRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Hand off a conversation to human staff."""
    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    member = workspace_service.get_member(
        db, conversation.workspace_id, current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )

    updated = conversation_service.set_handoff(db, conversation, current_user.id)

    if handoff_data.reason:
        conversation_service.add_message(
            db,
            conversation_id,
            sender_type="system",
            content=f"Handoff requested: {handoff_data.reason}",
        )

    return updated


# ============ Close Conversation ============

@router.post("/{conversation_id}/close", response_model=ConversationResponse)
def close_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Close a conversation."""
    conversation = conversation_service.get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )
    member = workspace_service.get_member(
        db, conversation.workspace_id, current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )
    return conversation_service.close_conversation(db, conversation)