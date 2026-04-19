import uuid

import pytest
from fastapi.testclient import TestClient
from app.database import get_db
from app.main import app
from app.models import Base, Article
from tests.test_db import get_db_test, engine, SessionLocal


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = get_db_test

    db = SessionLocal()
    db.add_all([
        Article(
            uuid=str(uuid.uuid4()),
            source="wikipedia",
            title="Artificial Intelligence",
            url="https://en.wikipedia.org/wiki/Artificial_Intelligence",
            content="Test content",
            author="Wikipedia"
        ),
        Article(
            uuid=str(uuid.uuid4()),
            source="reddit",
            title="Artificial Intelligence",
            url="https://reddit.com/wiki/Artificial_Intelligence",
            content="Test reddit content",
            author="John Doe"
        )
    ])
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)