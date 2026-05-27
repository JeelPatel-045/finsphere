import json
import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.chat_message import ChatMessage
from app.models.documents import Document
from app.services.chat_service import generate_ai_response

router = APIRouter()

ACTIVE_CONTEXT_FILE = "./uploads/active_context.json"


class ChatRequest(BaseModel):
    message: str


def _active_doc_id(db: Session) -> int | None:
    """Return DB id of the most recently uploaded document, if any."""
    if not os.path.exists(ACTIVE_CONTEXT_FILE):
        return None
    try:
        with open(ACTIVE_CONTEXT_FILE) as f:
            ctx = json.load(f)
        filename = ctx.get("filename")
        if not filename:
            return None
        doc = (
            db.query(Document)
            .filter(Document.filename == filename)
            .order_by(Document.created_at.desc())
            .first()
        )
        return doc.id if doc else None
    except Exception:
        return None


@router.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    response = generate_ai_response(request.message)

    # Persist messages to DB — silently skip if DB is unavailable
    try:
        doc_id = _active_doc_id(db)
        db.add(ChatMessage(document_id=doc_id, role="user", content=request.message))
        db.add(ChatMessage(document_id=doc_id, role="assistant", content=response))
        db.commit()
    except Exception:
        pass

    return {"response": response}


@router.get("/chat/history")
def get_history(document_id: int | None = None, db: Session = Depends(get_db)):
    try:
        if document_id is None:
            document_id = _active_doc_id(db)
        q = db.query(ChatMessage)
        if document_id:
            q = q.filter(ChatMessage.document_id == document_id)
        messages = q.order_by(ChatMessage.created_at).all()
        return [
            {
                "id":         m.id,
                "role":       m.role,
                "content":    m.content,
                "created_at": m.created_at.isoformat(),
            }
            for m in messages
        ]
    except Exception:
        return []


@router.delete("/chat/history")
def clear_history(document_id: int | None = None, db: Session = Depends(get_db)):
    try:
        q = db.query(ChatMessage)
        if document_id:
            q = q.filter(ChatMessage.document_id == document_id)
        q.delete()
        db.commit()
    except Exception:
        pass
    return {"ok": True}
