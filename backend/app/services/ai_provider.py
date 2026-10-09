"""
AI Provider Adapter — Provider-agnostic LLM interface.

This module provides a common interface for LLM providers.
Concrete providers (OpenAI, Gemini, Claude) can be added by subclassing
BaseAIProvider. The MockProvider is used during development without API keys.
"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
    ) -> str:
        """Generate a response given a list of messages.

        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            system_prompt: Optional system-level instruction.
            max_tokens: Maximum tokens in response.

        Returns:
            Assistant response text.
        """
        raise NotImplementedError


class MockAIProvider(BaseAIProvider):
    """
    Mock AI provider for development and testing.
    Returns deterministic responses without calling external APIs.
    """

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
    ) -> str:
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break

        # Simple keyword-based mock responses
        if any(word in user_message for word in ["hello", "hi", "হ্যালো", "হাই", "assalam", "salam"]):
            return "Hello! আমি MyGenie Assistant। আপনাকে কীভাবে সাহায্য করতে পারি?"

        if any(word in user_message for word in ["hour", "time", "khola", "খোলা", "সময়", "কখন"]):
            return "দোকান খোলার সময়: সকাল ৯টা থেকে রাত ৯টা পর্যন্ত (শুক্রবার বন্ধ)।"

        if any(word in user_message for word in ["price", "cost", "দাম", "কত", "মূল্য"]):
            return "দাম সম্পর্কে জানতে আমাদের product catalog দেখুন বা আমাদের staff-এর সাথে যোগাযোগ করুন।"

        if any(word in user_message for word in ["delivery", "ডেলিভারি", "পাঠানো"]):
            return "ঢাকার ভেতরে ফ্রি ডেলিভারি। ঢাকার বাইরে অতিরিক্ত চার্জ প্রযোজ্য।"

        if any(word in user_message for word in ["order", "অর্ডার", "কিনতে", "কিনব"]):
            return "অর্ডার করতে আপনার পণ্য এবং পরিমাণ জানান। আমি আপনাকে সাহায্য করব।"

        if any(word in user_message for word in ["booking", "বুকিং", "appointment", "অ্যাপয়েন্টমেন্ট"]):
            return "বুকিং করতে অনুগ্রহ করে তারিখ এবং সময় জানান। আমি availability check করব।"

        # Default response
        return (
            "আমি আপনার প্রশ্নটি বুঝতে পেরেছি। তবে এই বিষয়ে আমার নির্দিষ্ট তথ্য নেই। "
            "আমি আপনাকে আমাদের staff-এর সাথে সংযুক্ত করে দিচ্ছি। "
            "অথবা আপনি আমাদের FAQ দেখতে পারেন।"
        )


class GeminiProvider(BaseAIProvider):
    """
    Google Gemini provider. Requires GEMINI_API_KEY in .env.

    Uses a stable Gemini 2.x Flash model that is supported by the official SDK.
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
    ) -> str:
        try:
            import google.generativeai as genai
        except ImportError:
            raise RuntimeError(
                "google-generativeai package not installed. "
                "Run: pip install google-generativeai"
            )

        genai.configure(api_key=self.api_key)

        # Build prompt from messages
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(f"System: {system_prompt}")
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"{role.capitalize()}: {content}")

        full_prompt = "\n".join(prompt_parts)

        candidates = list(dict.fromkeys([self.model, "gemini-2.5-flash", "gemini-1.5-flash"]))
        last_error = None

        for model_name in candidates:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    full_prompt,
                    generation_config={"max_output_tokens": max_tokens},
                )
                return response.text
            except Exception as exc:  # pragma: no cover - network and provider issues
                last_error = exc
                message = str(exc).lower()
                if "not found" not in message and "not available" not in message:
                    raise

        if last_error is not None:
            raise last_error
        raise RuntimeError("Gemini request failed with no provider response")


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI provider. Requires OPENAI_API_KEY in .env.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
    ) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError(
                "openai package not installed. Run: pip install openai"
            )

        client = OpenAI(api_key=self.api_key)

        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        response = client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content
        return content.strip() if isinstance(content, str) else ""


# ============ Factory ============

def get_ai_provider() -> BaseAIProvider:
    """
    Factory function to get the configured AI provider.
    Falls back to MockAIProvider when the selected provider is unavailable,
    misconfigured, or the SDK dependency is missing.
    """
    from app.core.config import settings

    provider_name = getattr(settings, "AI_PROVIDER", "mock").lower().strip()

    if provider_name == "gemini":
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            return MockAIProvider()
        try:
            import google.generativeai  # noqa: F401
        except ImportError:
            return MockAIProvider()
        return GeminiProvider(api_key=api_key)
    elif provider_name == "openai":
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            return MockAIProvider()
        try:
            import openai  # noqa: F401
        except ImportError:
            return MockAIProvider()
        return OpenAIProvider(api_key=api_key)

    # Default: Mock provider
    return MockAIProvider()