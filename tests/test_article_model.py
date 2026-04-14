from app import Base, engine, SessionLocal
from app.models import Article


def test_article_model_creation():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        article = Article(
            uuid="123e4567-e89b-12d3-a456-426614174000",
            title="Test Title",
            article="Test Article",
            content="This is test content for the article model.",
            author="Stela",
            source="wikipedia"
        )

        existing = db.query(Article).filter_by(uuid=article.uuid).first()
        if existing:
            db.delete(existing)
            db.commit()

        db.add(article)
        db.commit()
        db.refresh(article)

        saved_article = db.query(Article).filter_by(uuid=article.uuid).first()

        assert saved_article is not None
        assert saved_article.title == "Test Title"
        assert saved_article.source == "wikipedia"
        assert saved_article.author == "Stela"
        assert saved_article.scraped_at is not None

        db.delete(saved_article)
        db.commit()
    finally:
        db.close()