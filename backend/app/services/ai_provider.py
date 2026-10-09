"""
AI Provider Adapter — Provider-agnostic LLM interface.

This module provides a common interface for LLM providers.
Concrete providers (OpenAI, Gemini, Claude) can be added by subclassing
BaseAIProvider. The MockProvider is used during development without API keys.
"""
import importlib
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
    Google Gemini provider. Requires GEMINI_API_KEY and the google-genai SDK.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 500,
    ) -> str:
        try:
            genai = importlib.import_module("google.genai")
        except ImportError:
            raise RuntimeError(
                "google-genai package is not installed. "
                "Install the backend dependencies before selecting Gemini."
            ) from None

        client = genai.Client(api_key=self.api_key)
        async_client = client.aio
        contents = [
            {
                "role": "model" if message.get("role") == "assistant" else "user",
                "parts": [{"text": message.get("content", "")}],
            }
            for message in messages
        ]
        config: Dict[str, object] = {"max_output_tokens": max_tokens}
        if system_prompt:
            config["system_instruction"] = system_prompt

        try:
            response = await async_client.models.generate_content(
                model=self.model,
                contents=contents,
                config=config,
            )
            text = response.text
            if not text or not text.strip():
                raise RuntimeError("Gemini returned an empty response")
            return text.strip()
        finally:
            await async_client.aclose()


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
            openai_module = importlib.import_module("openai")
        except ImportError:
            raise RuntimeError(
                "openai package not installed. Run: pip install openai"
            )

        client = openai_module.OpenAI(api_key=self.api_key)

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
    Return the explicitly configured AI provider.

    Mock responses are used only when AI_PROVIDER is set to "mock"; a
    misconfigured real provider must not appear to work by silently returning
    development responses.
    """
    from app.core.config import settings

    provider_name = getattr(settings, "AI_PROVIDER", "mock").lower().strip()

    if provider_name == "gemini":
        api_key = getattr(settings, "GEMINI_API_KEY", None)
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required when AI_PROVIDER=gemini")
        try:
            importlib.import_module("google.genai")
        except ImportError as exc:
            raise RuntimeError(
                "The google-genai package is required when AI_PROVIDER=gemini"
            ) from exc
        return GeminiProvider(
            api_key=api_key,
            model=getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash"),
        )

    if provider_name == "openai":
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when AI_PROVIDER=openai")
        try:
            importlib.import_module("openai")
        except ImportError as exc:
            raise RuntimeError(
                "The openai package is required when AI_PROVIDER=openai"
            ) from exc
        return OpenAIProvider(api_key=api_key)

    if provider_name == "mock":
        return MockAIProvider()

    raise ValueError(f"Unsupported AI_PROVIDER: {provider_name}")