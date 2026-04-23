import string
from datetime import date
from typing import List

from pydantic import BaseModel, Field


class ArticleOut(BaseModel):
    """Article Schema returned by the api"""
    uuid: str
    source: str
    title: str
    url: str
    content: str
    author: str


class ArticleList(BaseModel):
    """Paginated article wrapper with total count"""
    total_count: int
    articles: List[ArticleOut]

class SearchRequest(BaseModel):
    """Request body for semantic search."""
    query: str
    top_k: int = Field(default=5, ge=1, le=50)
    date_from: date | None = None
    source: str | None = None

class SearchResult(BaseModel):
    """Result returned by the api /search"""
    uuid: str
    title: str
    url: str
    source: str
    score: float
    content: str

class Source(BaseModel):
    """List of sources returned by rag for the top matching articles"""
    title: str
    url: str
    score: float


class RagResponse(BaseModel):
    """Response returned by /rag-search."""
    query: str
    answer: str
    sources: List[Source]
    confidence: float