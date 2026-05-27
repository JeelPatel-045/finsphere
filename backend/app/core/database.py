from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Dependency for FastAPI routes that need a DB session.
    Yields None when the database is unavailable — routes must handle None gracefully.
    """
    try:
        db = SessionLocal()
        try:
            # Quick connectivity check so we surface the error early
            db.execute(__import__("sqlalchemy").text("SELECT 1"))
            yield db
        finally:
            db.close()
    except Exception:
        yield None   # DB unavailable — let route decide what to return
