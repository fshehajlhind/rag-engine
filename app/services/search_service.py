import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.Client()
collection = client.get_or_create_collection(name="articles")
model = SentenceTransformer("all-MiniLM-L6-v2")

def search_articles(query, top_k=5):
    query_embeddings = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embeddings],
        n_results=top_k,
    )

    return format_query_results(results)

def format_query_results(results):
    formatted_results = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for id, document, metadata, distance in zip(ids, documents, metadatas, distances):
        formatted_results.append({
            "id": id,
            "document": document,
            "metadata": metadata,
        })

    return formatted_results

