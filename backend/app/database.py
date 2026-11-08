from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings
    
# 1. Thread configuration for SQLite
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
    
# 2. Create the Database Engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Set to True if you want to print all raw SQL queries to the terminal
)
    
# 3. Enforce Foreign Keys in SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
# 4. Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    
# 5. Declarative Base class (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    """Base class that all database models will inherit from."""
    pass
    
    
# 6. Database dependency generator
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