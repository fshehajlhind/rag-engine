import datetime
import logging
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT_PATH = Path(__file__).resolve().parents[2]
CHROMA_PATH = ROOT_PATH / "chroma_db"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="articles")
model = SentenceTransformer("all-MiniLM-L6-v2")


def search_articles(query, source=None, date_from=None, top_k=5):
    """Search the Chroma collection for k most similar articles to the query.
    Args:
        query: search query.
        top_k: number of similar articles to return.
        source: name of source(e.g wikipedia, reddit)
        date_from: filter articles scraped after this date.
    Returns:
        articles: list of formatted article objects: {uuid, title, url,
            source, snippet, and score}.
    """
    logging.info(f"Collection count in search: {collection.count()}", )
    query_embeddings = model.encode(query).tolist()
    query_params = {"query_embeddings": [query_embeddings], "n_results": top_k}
    if source:
        query_params["where"] = {"source": source}

    results = collection.query(**query_params)
    formatted_results = format_query_results(results)
    filtered_by_date_results = []
    if date_from:
        for article in formatted_results:
            article_date = article.get("date")
            if not article_date:
                continue
            try:
                article_date = datetime.datetime.fromisoformat(article_date).date()
                if article_date >= date_from:
                    filtered_by_date_results.append(article)
            except ValueError:
                continue
        return filtered_by_date_results[:top_k]
    return formatted_results[:top_k]


def format_query_results(results):
    """Converts CHroma query results to a list of formatted article objects."""
    logging.info(f"Formatting query results")

    formatted_results = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for id, document, metadata, distance in zip(ids, documents, metadatas, distances):
        formatted_results.append({
            "uuid": id,
            "title": metadata["title"],
            "url": metadata["url"],
            "source": metadata["source"],
            "date": metadata.get("date"),
            "content": metadata["content"][:2000],
            "score": 1 - distance,
        })

    return formatted_results
