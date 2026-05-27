from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String)
    transaction_type = Column(String)
    amount = Column(Float)
    quarter = Column(String)