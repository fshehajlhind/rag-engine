from app.services.search_service import search_articles

queries = [
    "machine learning",
    "python web development",
    "large language model"
]

for query in queries:
    print(f"\nQUERY: {query}")
    results = search_articles(query, top_k=3)

    if not results:
        print("No results found")
        continue

    for i, result in enumerate(results, start=1):
        print(f"\nResult {i}")
        print("UUID:", result["uuid"])
        print("Title:", result["title"])
        print("Source:", result["source"])
        print("URL:", result["url"])
        print("Score:", result["score"])
        print("Snippet:", result["snippet"])