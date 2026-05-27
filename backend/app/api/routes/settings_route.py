from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.models.user_settings import UserSettings

router = APIRouter(prefix="/settings")


class SettingsUpdate(BaseModel):
    currency:               Optional[str]   = None
    usd_to_inr_rate:        Optional[float] = None
    theme:                  Optional[str]   = None
    llm_provider:           Optional[str]   = None
    notifications_enabled:  Optional[bool]  = None
    email_notifications:    Optional[bool]  = None
    date_format:            Optional[str]   = None
    language:               Optional[str]   = None


def _get_or_create(db: Session) -> UserSettings:
    s = db.query(UserSettings).first()
    if not s:
        s = UserSettings()
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def _as_dict(s: UserSettings) -> dict:
    return {
        "currency":              s.currency,
        "usd_to_inr_rate":       s.usd_to_inr_rate,
        "theme":                 s.theme,
        "llm_provider":          s.llm_provider,
        "notifications_enabled": s.notifications_enabled,
        "email_notifications":   s.email_notifications,
        "date_format":           s.date_format,
        "language":              s.language,
    }


_DEFAULTS = {
    "currency": "INR", "usd_to_inr_rate": 83.0, "theme": "dark",
    "llm_provider": "groq", "notifications_enabled": True,
    "email_notifications": False, "date_format": "DD/MM/YYYY", "language": "en",
}

@router.get("")
def get_settings(db: Session = Depends(get_db)):
    try:
        return _as_dict(_get_or_create(db))
    except Exception:
        return _DEFAULTS.copy()


@router.patch("")
def update_settings(req: SettingsUpdate, db: Session = Depends(get_db)):
    try:
        s = _get_or_create(db)
        for field, value in req.dict(exclude_none=True).items():
            setattr(s, field, value)
        db.commit()
        db.refresh(s)
        return _as_dict(s)
    except Exception:
        return _DEFAULTS.copy()
