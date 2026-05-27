"""
Shared LLM instance for all FinSphere AI agents.

Switch provider by setting LLM_PROVIDER in ai-services/.env:
  LLM_PROVIDER=groq        → Groq (fast, has daily token limit)
  LLM_PROVIDER=openrouter  → OpenRouter free tier (default)

No code changes needed — just update the .env and restart.
"""

from dotenv import load_dotenv
import os

load_dotenv(override=True)

_provider = os.getenv("LLM_PROVIDER", "openrouter").lower()

# ── Groq ──────────────────────────────────────────────────────────────────────
if _provider == "groq":
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        model_name=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        temperature=0.3,
    )

# ── OpenRouter (default) ───────────────────────────────────────────────────────
else:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENROUTER_API_KEY", ""),
        model=os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
        base_url="https://openrouter.ai/api/v1",
        temperature=0.3,
    )
