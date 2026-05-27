from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import ask_finance_question

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    question: str

@router.post("/")
def finance_chat(request: ChatRequest):
    response = ask_finance_question(request.question)

    return {
        "success": True,
        "response": response
    }