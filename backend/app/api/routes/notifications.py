from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.notification import Notification

router = APIRouter(prefix="/notifications")


@router.get("")
def get_notifications(db = Depends(get_db)):
    if db is None:
        return []
    rows = (
        db.query(Notification)
        .order_by(Notification.created_at.desc())
        .limit(30)
        .all()
    )
    return [
        {
            "id":         n.id,
            "title":      n.title,
            "message":    n.message,
            "type":       n.type,
            "is_read":    n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in rows
    ]


@router.get("/unread-count")
def unread_count(db = Depends(get_db)):
    if db is None:
        return {"count": 0}
    count = db.query(Notification).filter(Notification.is_read == False).count()
    return {"count": count}


@router.patch("/{notification_id}/read")
def mark_read(notification_id: int, db = Depends(get_db)):
    if db is None:
        return {"ok": True}
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if n:
        n.is_read = True
        db.commit()
    return {"ok": True}


@router.patch("/read-all")
def mark_all_read(db = Depends(get_db)):
    if db is None:
        return {"ok": True}
    db.query(Notification).update({"is_read": True})
    db.commit()
    return {"ok": True}


@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db = Depends(get_db)):
    if db is None:
        return {"ok": True}
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if n:
        db.delete(n)
        db.commit()
    return {"ok": True}


def push_notification(db, title: str, message: str = "", type: str = "info"):
    """Helper used by other routes to create a notification."""
    if db is None:
        return
    n = Notification(title=title, message=message, type=type)
    db.add(n)
    db.commit()
