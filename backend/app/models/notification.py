from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from datetime import datetime
from app.core.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String, nullable=False)
    message    = Column(Text)
    type       = Column(String, default="info")    # info | success | warning | error
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
