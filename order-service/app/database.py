from collections.abc import Generator

from app.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

settings = get_settings()
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
