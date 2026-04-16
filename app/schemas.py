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


class SearchResult(BaseModel):
    """Result returned by the api"""
    uuid: str
    title: str
    url: str
    source: str
    score: float
    snippet: str

class RagSource(BaseModel):
    """Rag response item """
    title: str
    url: str
    score: float

class RagResponse(BaseModel):
    """Response returned by /rag-search."""
    query: str
    answer: str
    sources: List[RagSource]
    confidence: float