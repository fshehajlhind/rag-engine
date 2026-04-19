import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Article, Base

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_test():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    # Base.metadata.drop_all(bind=engine)
