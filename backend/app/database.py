from datetime import datetime, timezone

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import BACKEND_DIR, settings


def _resolve_database_url(url: str) -> str:
    """
    Với SQLite, đổi đường dẫn tương đối (sqlite:///./x.db) thành đường dẫn tuyệt đối
    tính từ thư mục backend/, để chạy uvicorn hay scripts ở thư mục nào cũng dùng chung 1 file DB.
    """
    prefix = "sqlite:///"
    if url.startswith(prefix) and not url.startswith(prefix + "/") and ":memory:" not in url:
        return f"{prefix}{(BACKEND_DIR / url[len(prefix):]).resolve()}"
    return url


DATABASE_URL = _resolve_database_url(settings.DATABASE_URL)
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# 1. Create the Database Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
    echo=False,  # Set to True if you want to print all raw SQL queries to the terminal
)

# 2. Enforce Foreign Keys in SQLite (mặc định SQLite TẮT khóa ngoại -> ondelete CASCADE/RESTRICT sẽ không chạy)
if IS_SQLITE:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# 3. Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 4. Declarative Base class (SQLAlchemy 2.0 style)
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
