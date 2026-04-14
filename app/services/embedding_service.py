import chromadb
from sentence_transformers import SentenceTransformer

from app.models import Article

client = chromadb.Client()
collection = client.get_or_create_collection(name="articles")


def embed_all_articles(db_session):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    articles = db_session.query(Article).all()

    inserted = 0
    skipped = 0

    for article in articles:
        existing = collection.get(id=article.uuid)
        if existing:
            skipped += 1
            continue
        embedding_input = article.title + " " + article.content
        embedded = model.encode(embedding_input)

        collection.add(ids=[article.uuid], embeddings=[embedded], documents=[embedding_input],
                       metadatas=[{"title": article.title, "source": article.source,
                                  "url": article.url}])
        inserted += 1

    print(f"Inserted {inserted} articles, skipped {skipped}")
