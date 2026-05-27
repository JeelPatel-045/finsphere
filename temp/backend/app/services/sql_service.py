from sqlalchemy import text
from app.core.database import engine
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_sql(question: str):
    prompt = f"""
    Convert the following finance question into SQL.

    Question: {question}

    Table: transactions
    Columns:
    id, account_name, transaction_type, amount, quarter
    """

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


def run_sql(query: str):
    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = [dict(row._mapping) for row in result]

    return rows