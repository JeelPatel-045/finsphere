from core.llm import llm


def sql_agent(query: str) -> str:
    """Convert a natural-language finance question into a PostgreSQL query."""
    prompt = f"""
You are a PostgreSQL expert for an enterprise financial database.

Table: transactions
Columns: id, account_name, transaction_type, amount, quarter, risk_score, vendor_name, payment_date

Convert the following question into a valid PostgreSQL query.
Return ONLY the SQL — no explanation, no markdown fences.

Question:
{query}
"""
    response = llm.invoke(prompt)
    return response.content
