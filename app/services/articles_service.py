import logging

from sqlalchemy import func

from app.models import Article
from sqlalchemy.orm import Session


def get_articles_dict(db: Session, page: int = 1,
                      page_size: int | None = None) -> dict:
    articles_query = db.query(Article).order_by(Article.title)

    if page_size is not None:
        articles = articles_query.offset((page - 1) * page_size).limit(page_size).all()
    else:
        articles = articles_query.all()
    total_count = db.query(Article).count()
    logging.info("Fetched %d articles", total_count)

    return {
        "total_count": total_count,
        "articles": [article_to_dict(article) for article in articles],
    }


def get_article_dict_by_id(db: Session, article_id: str) -> dict | None:
    article = db.query(Article).filter(Article.uuid == article_id).first()

    if article is None:
        return None

    return article_to_dict(article)


def article_to_dict(article: Article) -> dict:
    return {
        "uuid": article.uuid,
        "title": article.title,
        "url": article.url,
        "source": article.source,
        "content": article.content,
        "author": article.author,
    }


def get_article_stats(db: Session) -> dict:
    grouped_articles = db.query(Article.source, func.count(Article.uuid)).group_by(Article.source).all()
    logging.info("Grouped articles by source %s", grouped_articles)
    return {
        "stats": [
            {"count": count,
             "source": source,
             }
            for source, count in grouped_articles
        ]
    }
