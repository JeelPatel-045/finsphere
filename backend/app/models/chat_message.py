from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id          = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    role        = Column(String, nullable=False)   # "user" | "assistant"
    content     = Column(Text, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)
