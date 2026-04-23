# Simple RAG Search Engine

A RAG(Retrieval-Augmented Generation) Search Engine which scrapes articles from public websites, exposes a REST API
where users can ask questions. The answers are generated using an AI model and based entirely on the retrieved content.

## Main Features

- Scrapes articles from public websites (Wikipedia, Reddit, Devto).
- Stores article data in the database(url, content summary, author, source).
- Builds embeddings and indexes them in ChromaDB
- Exposes REST API endpoints

## Local Setup

1. Clone the repository
    ```bash
   git clone https://github.com/fshehajlhind/rag-engine.git
   ```
3. Install dependencies
    ```bash
    pip install -r requirements.txt
   ```
3. Run the ingestion step which scrapes all the websites(Wikipedia, Reddit, Devto) and stores data as CSVs and loads them in the database.
    ```bash
    python -m app.services.ingestion_service
   ``` 
   To select the sources you want to run(e.g Wikipedia, Reddit) you must add the arg --source followed by sources :
separated by space, like below:
    ```bash
    python -m app.services.ingestion_service --source source1 source2
    ```
4. Run the embedding step to generate embeddings from the articles stored in DB and index them in the ChromaDB
    ```bash
      python -m app.services.embedding_service
   ```
5. Start the application
    ```bash
   uvicorn app.main:app --reload --port 8080
     ```
6. Open the API documentation which includes the list of endpoints at http://localhost:8080/docs

7. Add the LLM environment variables as in the template .env.example. Make sure Ollama is running and the model is 
downloaded. You can check the loaded models here: http://{OLLAMA_BASE_URL}/api/tags

## Testing
To run all automated tests 
```bash
  python -m pytest tests/test_api.py 
```
## Docker setup
1. Build the image and start the app container
```bash
   docker-compose up --build
```
2. The API Schema can be viewed at http://localhost:8000/docs