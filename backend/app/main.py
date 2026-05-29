import os
import shutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.database import Base, engine

# Import all models so SQLAlchemy registers them before create_all
import app.models.user          # noqa: F401
import app.models.documents     # noqa: F401
import app.models.chat_message  # noqa: F401
import app.models.notification  # noqa: F401
import app.models.user_settings # noqa: F401

app = FastAPI(
    title="FinSphere AI Backend",
    version="2.0.0",
    description="Enterprise AI-powered financial intelligence platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins="allow_origins",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


UPLOADS_DIR = "./uploads"


@app.on_event("startup")
def startup():
    # ── 1. Create/clear uploads directory ────────────────────────────────────
    if os.path.exists(UPLOADS_DIR):
        cleared = 0
        for entry in os.listdir(UPLOADS_DIR):
            path = os.path.join(UPLOADS_DIR, entry)
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    cleared += 1
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    cleared += 1
            except Exception as exc:
                print(f"[startup] Could not delete {path}: {exc}")
        print(f"[startup] Cleared {cleared} item(s) from uploads/")
    else:
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        print("[startup] Created uploads/ directory")

    # ── 2. Create DB tables (best-effort) ────────────────────────────────────
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[startup] DB not available: {e.__class__.__name__} — will retry on first request")


app.include_router(api_router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FinSphere Backend", "version": "2.0.0"}


allow_origins=[
    "http://localhost:3000",
    "https://finsphere-ai.vercel.app",   # ← add this
    os.getenv("FRONTEND_URL", ""),        # ← and this for flexibility
]