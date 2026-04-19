import logging
import os
from statistics import mean

import requests

from app.models import Article
from app.services.search_service import search_articles


def create_content(articles: list[Article]):
    context_articles = []
    for article in articles:
        context_articles.append(
            f"Title: {article['title']}\n"
            f"Source: {article['source']}\n"
            f"URL: {article['url']}\n"
            f"Content: {article['content']}\n"
        )
    context = ' '.join(context_articles)
    return context


def call_llm(prompt) -> str:
    if os.getenv("LLM_PROVIDER") == "offline":
        logging.info("Using offline mode")
        ollama_url = os.getenv("LLM_URL") + "/api/generate"
        ollama_model = os.getenv("LLM_MODEL")
        try:
            response = requests.post(ollama_url, json=
            {"model": ollama_model, "prompt": prompt})
            response.raise_for_status()
        except requests.Timeout:
            logging.error("Request timed out")
            return ""
        except requests.HTTPError as e:
            logging.error("HTTP error status: %d, %s", e.response.status_code, e.response.reason)
            return ""
        try:
            data = response.json()
        except ValueError:
            logging.error("Invalid JSON")
            return ""
        return data.response
    else:
        return ""


async def rag_search_service(query: str, top_k: int = 5):
    results = search_articles(query, top_k)
    if not results:
        return {
            "query": query,
            "sources": [],
            "answer": "No articles found for this query.",
            "confidence": 0
        }

    context = create_content(results)
    llm_prompt = f"""
    You have been provided with multiple documents. Your task is to synthesize the
information from these documents to answer the question. When you use information
from a document, cite it using its identifier.
    Question: {query}
    Context: {context}
    Answer:
    """
    answer = call_llm(llm_prompt)

    scores = [article["score"] for article in results]
    confidence = mean(scores) if scores else 0

    return {
        "query": query,
        "answer": answer,
        "sources": [article["source"] for article in results],
        "confidence": confidence
    }
