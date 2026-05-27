from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float
from datetime import datetime
from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id               = Column(Integer, primary_key=True, index=True)
    filename         = Column(String, nullable=False)
    content_type     = Column(String)
    file_type        = Column(String)
    size_bytes       = Column(Integer, default=0)
    status           = Column(String, default="processed")
    document_type    = Column(String, default="unknown")
    company_name     = Column(String)
    period           = Column(String)
    summary          = Column(Text)
    currency         = Column(String, default="USD")
    key_metrics      = Column(JSON, default=list)
    insights         = Column(JSON, default=list)
    risks            = Column(JSON, default=list)
    positives        = Column(JSON, default=list)
    raw_numbers      = Column(JSON, default=dict)
    all_extracted    = Column(JSON, default=dict)
    suggested_qs     = Column(JSON, default=list)
    raw_text         = Column(Text)
    file_path        = Column(String)
    created_at       = Column(DateTime, default=datetime.utcnow)
