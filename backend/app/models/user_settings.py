from sqlalchemy import Column, Integer, String, Boolean, Float
from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id                     = Column(Integer, primary_key=True, index=True)
    currency               = Column(String, default="INR")
    usd_to_inr_rate        = Column(Float, default=83.0)
    theme                  = Column(String, default="dark")
    llm_provider           = Column(String, default="groq")
    notifications_enabled  = Column(Boolean, default=True)
    email_notifications    = Column(Boolean, default=False)
    date_format            = Column(String, default="DD/MM/YYYY")
    language               = Column(String, default="en")
