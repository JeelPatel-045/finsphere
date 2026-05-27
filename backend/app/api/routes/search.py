from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.documents import Document
from app.models.chat_message import ChatMessage

router = APIRouter(prefix="/search")


@router.get("")
def search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    try:
        term = f"%{q.lower()}%"

        docs = (
            db.query(Document)
            .filter(
                Document.filename.ilike(term)
                | Document.summary.ilike(term)
                | Document.company_name.ilike(term)
                | Document.document_type.ilike(term)
            )
            .order_by(Document.created_at.desc())
            .limit(10)
            .all()
        )

        chats = (
            db.query(ChatMessage)
            .filter(ChatMessage.content.ilike(term))
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
            .all()
        )

        return {
            "documents": [
                {
                    "id":            d.id,
                    "filename":      d.filename,
                    "document_type": d.document_type,
                    "summary":       (d.summary or "")[:120],
                    "company_name":  d.company_name,
                    "created_at":    d.created_at.isoformat() if d.created_at else None,
                }
                for d in docs
            ],
            "chat_messages": [
                {
                    "id":         c.id,
                    "role":       c.role,
                    "content":    c.content[:200],
                    "doc_id":     c.document_id,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in chats
            ],
        }
    except Exception:
        return {"documents": [], "chat_messages": []}
