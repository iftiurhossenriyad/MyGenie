"""
AI Chat Service — Grounded AI responses with workspace FAQ context.

The AI assistant is treated as an interface to the application, not as the
source of truth for business records. Business answers are grounded in the
workspace's published FAQs and business profile.
"""
import logging
from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from app.models.faq import FAQ
from app.models.business_profile import BusinessProfile
from app.models.message import Message
from app.models.conversation import Conversation
from app.services.ai_provider import get_ai_provider


logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are MyGenie, a helpful AI assistant for small businesses in Bangladesh.

Your role:
- Help customers with questions about products, hours, delivery, orders, and bookings.
- Respond in the SAME language the user writes in (Bangla, English, or mixed Bangla-English).
- Be concise, friendly, and professional.
- NEVER invent prices, policies, stock, or delivery times. If information is unavailable, say so and offer to connect with a human staff member.
- For orders and bookings, gather the required details but confirm with the user before creating records.
- If the user is upset, confused, or asks for something outside approved business knowledge, suggest human handoff.

Context about the business is provided below. Use it to answer accurately.
"""


def build_faq_context(db: Session, workspace_id: int, user_message: str) -> str:
    """
    Build FAQ context string for a workspace.
    For MVP, include all published FAQs. Future: use embedding-based retrieval.
    """
    faqs = (
        db.query(FAQ)
        .filter(FAQ.workspace_id == workspace_id)
        .filter(FAQ.status == "published")
        .limit(20)
        .all()
    )

    if not faqs:
        return "No published FAQs available."

    lines = ["Published FAQs:"]
    for faq in faqs:
        lines.append(f"Q: {faq.question}")
        lines.append(f"A: {faq.answer}")
        if faq.question_en and faq.answer_en:
            lines.append(f"Q (EN): {faq.question_en}")
            lines.append(f"A (EN): {faq.answer_en}")
        lines.append("")

    return "\n".join(lines)


def build_business_context(db: Session, workspace_id: int) -> str:
    """Build business profile context."""
    profile = (
        db.query(BusinessProfile)
        .filter(BusinessProfile.workspace_id == workspace_id)
        .first()
    )

    if not profile:
        return "No business profile available."

    lines = [
        "Business Information:",
        f"- Name: {profile.business_name}",
    ]
    if profile.description:
        lines.append(f"- Description: {profile.description}")
    if profile.address:
        lines.append(f"- Address: {profile.address}")
    if profile.phone:
        lines.append(f"- Phone: {profile.phone}")
    if profile.opening_hours:
        lines.append(f"- Opening Hours: {profile.opening_hours}")
    if profile.delivery_info:
        lines.append(f"- Delivery: {profile.delivery_info}")
    if profile.policies:
        lines.append(f"- Policies: {profile.policies}")

    return "\n".join(lines)


def build_conversation_history(
    db: Session, conversation_id: int, limit: int = 10
) -> List[Dict[str, str]]:
    """Build recent conversation history for LLM context."""
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )

    # Reverse to chronological order
    messages = list(reversed(messages))

    history = []
    for msg in messages:
        if msg.sender_type == "user":
            role = "user"
        elif msg.sender_type == "assistant":
            role = "assistant"
        elif msg.sender_type == "staff":
            role = "assistant"
        else:
            continue
        history.append({"role": role, "content": msg.content})

    return history


async def generate_ai_response(
    db: Session,
    conversation: Conversation,
    user_message: str,
) -> str:
    """
    Generate an AI response for a user message in a conversation.
    Grounds the response in the workspace's FAQs and business profile.
    """
    # 1. Build grounded context
    business_context = build_business_context(db, conversation.workspace_id)
    faq_context = build_faq_context(db, conversation.workspace_id, user_message)

    # 2. Build full system prompt
    full_system_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"{business_context}\n\n"
        f"{faq_context}\n\n"
        f"Respond in the user's language (Bangla, English, or mixed)."
    )

    # 3. Build conversation history
    history = build_conversation_history(db, conversation.id, limit=10)

    # 4. Ensure the current user message is included
    if not history or history[-1].get("content") != user_message:
        history.append({"role": "user", "content": user_message})

    # 5. Call the AI provider
    provider = get_ai_provider()
    try:
        response = await provider.generate_response(
            messages=history,
            system_prompt=full_system_prompt,
            max_tokens=500,
        )
        return response
    except Exception:
        logger.exception("AI provider failed while generating a response")
        # Deterministic fallback
        return (
            "দুঃখিত, এই মুহূর্তে আমি উত্তর দিতে পারছি না। "
            "অনুগ্রহ করে কিছুক্ষণ পরে আবার চেষ্টা করুন, অথবা আমাদের staff-এর সাথে যোগাযোগ করুন।"
        )