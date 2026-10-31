from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.core.logging import logger
from app.database.base import Base

# Configure database engine
db_url = settings.DATABASE_URL

# Handle SQLite vs PostgreSQL arguments
connect_args = {}
if "sqlite" in db_url:
    connect_args["check_same_thread"] = False
else:
    connect_args["connect_timeout"] = 3

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        pool_pre_ping=True
    )
    # Test connection
    with engine.connect() as conn:
        logger.info(f"Database connected successfully to {db_url.split('@')[-1] if '@' in db_url else 'local db'}")
except Exception as e:
    logger.warning(f"Could not connect to configured DATABASE_URL: {e}. Falling back to SQLite for local development.")
    fallback_url = "sqlite:///./screening_local.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables in database."""
    Base.metadata.create_all(bind=engine)
