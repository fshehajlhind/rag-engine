import asyncio
import logging
import os

import httpx
from dotenv import load_dotenv

from app.services.search_service import search_articles

load_dotenv()


def create_context(articles: list[dict])-> str:
    """Returns the list of top articles as a context string
    Args:
        articles: List of articles
     Returns:
           A context string consisting of: title, url and content.
    """
    context_articles = []
    for article in articles:
        context_articles.append(
            f"Title: {article['title']}\n"
            f"URL: {article['url']}\n"
            f"Content: {article['content']}\n"
        )
    context = '\n'.join(context_articles)
    return context


async def call_llm(prompt: str, articles: list[dict]) -> str:
    ollama_url = os.getenv("OLLAMA_URL")
    model = os.getenv("OLLAMA_MODEL")

    if not ollama_url or not model:
        logging.info("LLM not configured")
        logging.info("Most relevant article %s", articles[0]['title'])
        return ""

    api_key = os.getenv("OLLAMA_API_KEY")
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(ollama_url + "/api/generate", headers=headers,
                                     json={"model": model, "prompt": prompt, "stream": False})
            response.raise_for_status()
    except httpx.TimeoutException:
        logging.error("Request timed out")
        return ""
    except httpx.HTTPStatusError as e:
        logging.error("Error status: %d  %s", e.response.status_code, e.response.text)
        return ""
    try:
        data = response.json()
    except ValueError:
        logging.error("Invalid JSON")
        return ""
    return data.get("response", "")


def retrieve_sources(results: list[dict]) -> list[dict]:
    return [
        {
            "title": item["title"],
            "url": item["url"],
            "score": item["score"],
        } for item in results
    ]

def generate_fallback_answer(top_article: dict) -> str:
    return f"Summary of the most relevant article: \n Title: {top_article['title']} \n {top_article['content'][:500]}"

async def rag_search_service(query: str, source: str = None, date_from=None, top_k: int = 5):
    """
    Builds the context from the top k matching articles and retrieves an answer from the LLM
    Args:
        query: Prompt entered by user
        source: Source filter(e.g., Search only articles from Wikipedia)
        date_from: Filter by scraped date
        top_k: Number of top results matching
    :return:
        A dict consisting of: query, list of matching sources, LLM response and
    """
    results = await asyncio.to_thread(search_articles, query, source, date_from, top_k)
    if not results:
        return {
            "query": query,
            "sources": [],
            "answer": "No articles found for this query.",
            "confidence": 0
        }

    context = create_context(results)
    logging.info("Created context %s", context)

    llm_prompt = f"""
    You have been provided with multiple articles. Your task is to answer the question based entirely on the context below.
    Instruction: 
    1. No outside knowledge
    2. Use only the provided context to answer the query.
    3. If the context is not enough to answer the question say that.
    4. Cite the titles of the articles you used as source in the answer.
    Question: {query}
    Context: {context}
    Answer:
    """
    answer = await call_llm(llm_prompt, results)
    logging.info("LLM answer: %s", answer)
    sources = retrieve_sources(results)

    confidence = results[0]["score"]
    logging.info("Confidence: %f", confidence)
    if not answer:
        return {
            "query": query,
            "sources": sources,
            "answer": generate_fallback_answer(results[0]),
            "confidence": confidence
        }
    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "confidence": confidence
    }
