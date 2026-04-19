import logging

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Article
from app.schemas import ArticleList, ArticleOut, SearchRequest, SearchResult, RagResponse
from app.services.rag import rag_search_service
from app.services.search_service import search_articles

router = APIRouter()


@router.get("/health")
def health():
    """Health check endpoint."""
    return {"message": "OK"}


@router.get("/articles", response_model=ArticleList)
def get_articles(page: int = Query(1, ge=1),
                 page_size: int|None = Query(None, ge=1, le=50),
                 db: Session = Depends(get_db)):
    """ Returns the paginated list of articles.
     Args:
        page (int): Page number >= 1.
        page_size (int): Number of articles to return per page.
        db: Database session.
    Returns:
          total_count (int): Total number of articles.
          articles (List[ArticleOut]): List of articles.
    """
    if page_size is None:
        articles = db.query(Article).all()
    else:
        articles = db.query(Article).offset((page - 1) * page_size).limit(page_size).all()
    total_count = db.query(Article).count()
    logging.info(f"Fetched %d articles", total_count)
    return {
        "total_count": total_count,
        "articles": articles,
    }


@router.get("/articles/{article_id}", response_model=ArticleOut
    , responses={404: {
        "description": "Article not found",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Article not found"
                }
            }
        }}})
def get_article_by_id(article_id: str, db: Session = Depends(get_db)):
    """Returns article for the given id
    Args:
        article_id: uuid of the article.
        db: Database session.
    Returns:
        Article: Matching article from the database.
     Raises:
        HTTPException: If the article is not found.
    """
    article = db.query(Article).filter(Article.uuid == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    logging.info("Fetched article with id: %s , url: %s, title: %s",
                 article_id, article.url, article.title)
    return article


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Returns total articles for each source.
     Args:
        db: Database session.
     Returns:
         dict: Dictionary of article counts for each source together with teh source.
    """
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


@router.post("/search", response_model=list[SearchResult])
def search(request: SearchRequest):
    """Returns top k search results for the given query."""
    return search_articles(request.query, request.source, request.top_k)


@router.post("/rag-search", response_model=RagResponse)
async def rag_search(request: SearchRequest):
    """Returns LLM response for the given query based on retrieved articles."""
    return await rag_search_service(request.query, top_k=request.top_k)
