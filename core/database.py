from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,   # avoid Supabase idle-closing stale conns
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from shared.database import models