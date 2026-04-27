import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Depends, Query, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article
from app.schemas import ArticleList, ArticleOut, SearchRequest, SearchResult, RagResponse
from app.services.articles_service import get_articles_dict, get_article_dict_by_id, get_article_stats
from app.services.export_service import export_files
from app.services.rag_service import rag_search_service
from app.services.search_service import search_articles

router = APIRouter()


@router.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "OK"}


@router.get("/articles", response_model=ArticleList)
def get_articles(page: int = Query(1, ge=1),
                 page_size: int | None = Query(None, ge=1, le=50),
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
    return get_articles_dict(db, page, page_size)


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
    article = get_article_dict_by_id(db=db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    logging.info("Fetched article with id: %s , url: %s, title: %s",
                 article_id, article["url"], article["title"])
    return article


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Returns total articles for each source.
     Args:
        db: Database session.
     Returns:
         dict: Dictionary of article counts for each source together with teh source.
    """
    return get_article_stats(db)


@router.post("/search", response_model=list[SearchResult])
def search(request: SearchRequest):
    """Returns top k search results for the given query.
       Args:
            query: query given by users
            top_k: top k search results
            date_from: search articles from a given date
            source: search articles give by source
       Returns:
            List with search results.
    """
    return search_articles(request.query, request.source, request.date_from, request.top_k)


@router.post("/rag-search", response_model=RagResponse)
async def rag_search(request: SearchRequest):
    """Returns LLM response for the given query based on retrieved articles."""
    return await rag_search_service(request.query, request.source, request.date_from, top_k=request.top_k)


@router.get("/export")
def export_articles(output_format: Literal["csv", "jsonl"] = Query("csv"), db: Session = Depends(get_db)):
    """Exports articles into a CSV or jsonl file.
    Args:
        db: Database session.
        output_format (Literal["csv", "jsonl"]): Output format to export.
    Returns:
         dict:
    """
    logging.info("Exporting articles in %s format...", output_format)

    content, media_type = export_files(output_format, db)
    return Response(
        content=content, media_type=media_type,  headers={
            "Content-Disposition": f"attachment; filename=articles.{output_format}"
        },
    )
