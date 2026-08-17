from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

from app.core.config import settings

db_engine = create_engine(url=settings.DATABASE_URL)

Base = declarative_base()
SessionLocal = sessionmaker(bind=db_engine)