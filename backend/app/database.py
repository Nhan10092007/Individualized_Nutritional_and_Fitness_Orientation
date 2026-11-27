from datetime import datetime, timezone

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import BACKEND_DIR, settings


def _resolve_database_url(url: str) -> str:
    """Đảm bảo URL PostgreSQL luôn dùng driver psycopg (v3)."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url
    


DATABASE_URL = _resolve_database_url(settings.DATABASE_URL)

# 1. Create the Database Engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,  # Set to True if you want to print all raw SQL queries to the terminal
)

# 2. Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 3. Declarative Base class (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    """Base class that all database models will inherit from."""
    pass


def utcnow() -> datetime:
    """Thời điểm hiện tại theo UTC (thay cho datetime.utcnow đã bị deprecated)."""
    return datetime.now(timezone.utc)


def init_db() -> None:
    """Tạo toàn bộ bảng từ các model (thay cho file schema.sql)."""
    import app.models  # noqa: F401  # đăng ký toàn bộ model vào Base.metadata

    Base.metadata.create_all(bind=engine)


# 5. Database dependency generator
def get_db():
    """
    Yields a database session per HTTP request.
    Automatically closes the session when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
