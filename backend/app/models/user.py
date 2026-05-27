from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, index=True, nullable=False)
    name            = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="analyst")
    avatar_color    = Column(String, default="#3B82F6")
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
