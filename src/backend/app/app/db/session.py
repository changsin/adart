from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True, pool_size=20, max_overflow=20
)
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
