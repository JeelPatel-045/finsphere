"""
FinSphere LLM Factory
=====================
Single source of truth for the LLM client used across the entire backend.

To switch provider, change LLM_PROVIDER in backend/.env:
  LLM_PROVIDER=groq        → uses Groq (llama-3.3-70b-versatile, fast, has daily token limit)
  LLM_PROVIDER=openrouter  → uses OpenRouter free tier (meta-llama/llama-3.3-70b-instruct:free)

No code changes needed — just update the .env and restart the server.
"""

from langchain_core.language_models.chat_models import BaseChatModel
from app.core.config import settings


def get_llm(temperature: float = 0.1, max_tokens: int = 2048) -> BaseChatModel:
    """Return the configured LLM instance.

    Args:
        temperature: Sampling temperature (0 = deterministic, 1 = creative).
        max_tokens:  Max output tokens.

    Returns:
        A LangChain chat model instance ready to invoke.
    """
    provider = settings.LLM_PROVIDER

    # ── Groq ──────────────────────────────────────────────────────────────────
    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # ── OpenRouter (default) ───────────────────────────────────────────────────
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        openai_api_key=settings.OPENROUTER_API_KEY,
        model=settings.OPENROUTER_MODEL,
        base_url=settings.OPENROUTER_BASE_URL,
        temperature=temperature,
        max_tokens=max_tokens,
    )
