from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Audit(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    risk_level = Column(String)
    description = Column(String)
    score = Column(Float)