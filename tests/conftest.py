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
            content="Artificial intelligence (AI) is the capability of computational systems to perform tasks typically associated with human intelligence,"
                    " such as learning, reasoning, problem-solving, perception, and decision-making. It is a field of research in engineering,"
                    " mathematics and computer science that develops and studies methods and software that enable machines"
                    " to perceive their environment and use learning and intelligence to take actions that maximize their chances of achieving defined goals.",
            author="Wikipedia"
        ),
        Article(
            uuid=str(uuid.uuid4()),
            source="reddit",
            title="AI — weekly megathread!",
            url="https://www.reddit.com/r/artificial/comments/12uaxy0/ai_weekly_megathread/",
            content="Stability AI released an open-source language model, StableLM that generates both code and text and is available in 3 billion and 7 billion parameters. The model is trained on a new dataset built on The Pile dataset, but three times larger with 1.5 trillion tokens. [Details | GitHub | HuggingFace Spaces].Synthesis AI has developed a text-to-3D technology that generates realistic, cinematic-quality digital humans for gaming, virtual reality, film, 3D simulations, etc., using generative AI and visual effects pipelines",
            author="John Doe"
        ),
        Article(
            uuid=str(uuid.uuid4()),
            source="reddit",
            title="Artemis II Launch To The Moon",
            url="https://reddit.com/wiki/Artificial_Intelligence",
            content="The mission can launch only when the moon, orbital paths, weather and Earth’s rotation line up safely."
                    "This is the third launch attempt for Artemis II, after the first attempt was scrubbed due to a liquid hydrogen leak during a practice countdown in early February, and the second attempt was cancelled when engineers discovered a helium flow issue in the rocket’s upper stage in early March",
            author="John Doe"
        )

    ])
    db.commit()
    db.close()

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)