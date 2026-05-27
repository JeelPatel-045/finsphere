from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import JWTError

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_token, decode_token
from app.models.user import User

router  = APIRouter(prefix="/auth")
_bearer = HTTPBearer(auto_error=False)


# ── Schemas ───────────────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    email:    str
    name:     str
    password: str

class LoginRequest(BaseModel):
    email:    str
    password: str

class UpdateProfileRequest(BaseModel):
    name:         Optional[str] = None
    avatar_color: Optional[str] = None


# ── Dependency ────────────────────────────────────────────────────────────────

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    db = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        payload = decode_token(credentials.credentials)
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def _user_dict(u: User) -> dict:
    return {
        "id":           u.id,
        "email":        u.email,
        "name":         u.name,
        "role":         u.role,
        "avatar_color": u.avatar_color,
        "created_at":   u.created_at.isoformat() if u.created_at else None,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/signup")
def signup(req: SignupRequest, db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    if db.query(User).filter(User.email == req.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=req.email.lower(),
        name=req.name,
        hashed_password=hash_password(req.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token({"sub": str(user.id)})
    return {"token": token, "user": _user_dict(user)}


@router.post("/login")
def login(req: LoginRequest, db = Depends(get_db)):
    if db is None:
        raise HTTPException(status_code=503, detail="Database unavailable")
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token({"sub": str(user.id)})
    return {"token": token, "user": _user_dict(user)}


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return _user_dict(current_user)


@router.patch("/me")
def update_profile(
    req: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
):
    if req.name:
        current_user.name = req.name
    if req.avatar_color:
        current_user.avatar_color = req.avatar_color
    if db is not None:
        db.commit()
        db.refresh(current_user)
    return _user_dict(current_user)
