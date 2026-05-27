from sqlalchemy import text

from app.core.llm_factory import get_llm   # ← single provider-agnostic factory
from app.core.database import engine

# Switch provider via LLM_PROVIDER in .env  (groq | openrouter)
llm = get_llm()

# ── Service functions ─────────────────────────────────────────────────────────

def generate_sql(question: str) -> str:
    """Convert a natural-language finance question into a PostgreSQL query."""
    prompt = (
        "You are a PostgreSQL expert for a financial database.\n\n"
        "Table: transactions\n"
        "Columns: id, account_name, transaction_type, amount, quarter, risk_score\n\n"
        f"Convert this question to SQL — return ONLY the SQL query, nothing else:\n{question}"
    )
    response = llm.invoke(prompt)
    return response.content


def run_sql(query: str) -> list[dict]:
    """Execute a raw SQL query and return results as a list of dicts."""
    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows   = [dict(row._mapping) for row in result]
    return rows
