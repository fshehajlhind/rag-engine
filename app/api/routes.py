import logging

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Article
from app.schemas import ArticleList, ArticleOut, SearchRequest, SearchResult
from app.services.search_service import search_articles

router = APIRouter()


@router.get("/health")
def health():
    """Health check endpoint."""
    return {"message": "OK"}


@router.get("/articles", response_model=ArticleList)
def get_articles(page: int = Query(1, ge=1),
                 page_size: int = Query(10, ge=1, le=50),
                 db: Session = Depends(get_db)):
    """Returns full list of articles."""
    articles = db.query(Article).offset((page - 1) * page_size).limit(page_size).all()
    total_count = db.query(Article).count()
    logging.info(f"Fetched %d articles", total_count)
    return {
        "total_count": total_count,
        "articles": articles,
    }


@router.get("/articles/{article_id}", response_model=ArticleOut)
def get_article_by_id(article_id: str, db: Session = Depends(get_db)):
    """Returns article by id"""
    article = db.query(Article).filter(Article.uuid == article_id).first()
    logging.info(f"Fetched article with id: {article_id} , url: {article.url}, title: {article.title}")
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Returns total articles by source."""
    grouped_articles = db.query(Article.source, func.count(Article.uuid)).group_by(Article.source).all()
    logging.info("Grouped articles by source ", grouped_articles)
    return {
        "stats": [
            { "count": count,
              "source": source,
             }
           for source, count in grouped_articles
        ]
    }


@router.post("/search", response_model=list[SearchResult])
def search(request: SearchRequest):
    """Returns top k search results for the given query."""
    return search_articles(request.query, request.top_k)
