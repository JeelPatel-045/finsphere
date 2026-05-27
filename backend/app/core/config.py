from dotenv import load_dotenv
import os

load_dotenv(override=True)   # override=True ensures .env always wins over stale env vars


class Settings:
    # ── Provider switch ────────────────────────────────────────────────────────
    # Set LLM_PROVIDER=groq  to use Groq
    # Set LLM_PROVIDER=openrouter  to use OpenRouter (free tier)
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter").lower()

    # ── Groq credentials (commented out — daily token limit reached) ───────────
    # GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    # GROQ_MODEL: str   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # ── OpenRouter credentials (active) ───────────────────────────────────────
    OPENROUTER_API_KEY: str  = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str    = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # ── Database ───────────────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/finsphere"
    )

    # ── Vector store ───────────────────────────────────────────────────────────
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", "./chroma_db")

    # ── AI microservice ────────────────────────────────────────────────────────
    AI_SERVICE_URL: str = os.getenv("AI_SERVICE_URL", "http://localhost:9000")


settings = Settings()
