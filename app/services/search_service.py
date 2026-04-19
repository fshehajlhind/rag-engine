import logging
from pathlib import Path

import chromadb
from chromadb import K
from chromadb.execution.expression import Eq, And
from sentence_transformers import SentenceTransformer

ROOT_PATH = Path(__file__).resolve().parents[2]
CHROMA_PATH = ROOT_PATH / "chroma_db"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="articles")
model = SentenceTransformer("all-MiniLM-L6-v2")


def search_articles(query, source=None, top_k=5):
    """Search the Chroma collection for k most similar articles to the query.
    Args:
        query: search query.
        top_k: number of similar articles to return.
        source: name of source(e.g wikipedia,reddit)
    Returns:
        articles: list of formatted article objects: {uuid, title, url,
            source, snippet, and score}.
    """
    logging.info(f"Collection count in search: {collection.count()}", )
    query_embeddings = model.encode(query).tolist()
    query_params = {
        "query_embeddings": [query_embeddings],
        "n_results": top_k
    }
    if source:
        query_params["where"] = {"source": source}
    results = collection.query(**query_params)
    return format_query_results(results)


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
            "content": metadata["content"][:2000],
            "score": 1 - distance,
        })

    return formatted_results
