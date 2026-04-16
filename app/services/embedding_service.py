import logging
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from app.models import Article

ROOT_PATH = Path(__file__).resolve().parents[2]
CHROMA_PATH = ROOT_PATH / "chroma_db"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name="articles")
logger = logging.getLogger(__name__)


def embed_all_articles(db_session):
    """ Embed all articles from DB and store uniques in the Chroma collection."""
    model = SentenceTransformer("all-MiniLM-L6-v2")
    articles = db_session.query(Article).all()

    inserted = 0
    skipped = 0

    for article in articles:
        existing = collection.get(ids=[article.uuid])
        if existing["ids"]:
            logging.info(f"Skipping article {article.uuid}")
            skipped += 1
            continue
        embedding_input = article.title + " " + article.content
        embedded = model.encode(embedding_input)

        collection.add(ids=[article.uuid], embeddings=[embedded], documents=[embedding_input],
                       metadatas=[{"title": article.title, "source": article.source,
                                  "url": article.url, "content": article.content}])
        inserted += 1
    logger.info("Collections number: %s", collection.count())
    logger.info(f"Inserted {inserted} articles, skipped {skipped}")
