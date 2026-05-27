from sqlalchemy import Column, Integer, Float, String
from app.core.database import Base

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String)
    predicted_revenue = Column(Float)