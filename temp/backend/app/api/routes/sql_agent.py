from fastapi import APIRouter
from pydantic import BaseModel
from app.services.sql_service import generate_sql, run_sql

router = APIRouter(prefix="/sql-agent", tags=["SQL Agent"])

class SQLRequest(BaseModel):
    question: str

@router.post("/")
def sql_agent(request: SQLRequest):
    sql_query = generate_sql(request.question)

    data = run_sql(sql_query)

    return {
        "generated_sql": sql_query,
        "results": data
    }