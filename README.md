# Simple RAG Search Engine

A RAG(Retrieval-Augmented Generation) search engine which scrapes articles from public websites, indexes them in 
ChromaDb and exposes a REST API where users can ask questions. The answers are generated using an AI model 
and based entirely on the retrieved content associate with top relevant sources.

## Main Features

- Scrapes articles from public websites (Wikipedia, Reddit, Devto).
- Stores article data in the database(url, content summary, author, source).
- Builds embeddings and indexes them in ChromaDB
- Exposes REST API endpoints

## Project Structure

```text
app/
├── api/            # API routes
├── services/       # ingestion, embedding, search and rag services
├── scrapers/       # scrapers for each website
├── models.py       # SQLAlchemy models
├── schemas.py      # Pydantic schemas
├── database.py     # DB setup 
└── main.py         # 

tests/              # automated tests
data/               # generated CSV files
```
## Prerequisites
- Python 3
- pip
- Docker
- Ollama with a downloaded model

## API Reference table
| Method | Endpoint                                        | Description                                      |
|--------|-------------------------------------------------|--------------------------------------------------|
| `GET`  | `/health`                                       | Health check endpoint                            |
| `GET`  | `/articles?page={page_number}&page_size={size}` | Returns paginated articles                       |
| `GET`  | `/articles/{article_id}`                        | Returns an article by UUID                       |
| `GET`  | `/stats`                                        | Returns number of articles for each source       |
| `POST` | `/search`                                       | Performs semantic search and finds top k similar |
| `POST` | `/rag-search`                                   | Returns an LLM answer with sources               |
| `GET`  | `/export?output_format={output_format}`         | Downloads articles as JSONL/CSV                  |

## Local Setup

1. Clone the repository
    ```bash
   git clone https://github.com/fshehajlhind/rag-engine.git
   ```
2. Create and activate virtual environment    
   ```bash
   python -m venv .venv
   ```
   ```bash
   .venv\Scripts\activate
   ```
3. Install dependencies
    ```bash
    pip install -r requirements.txt
   ```
4. Run the ingestion step which scrapes all the websites(Wikipedia, Reddit, Devto) and stores data as CSVs and loads them in the database.
    ```bash
    python -m app.services.ingestion_service
    ``` 
   To select the sources you want to run(e.g Wikipedia, Reddit, Dev.to) you must add the arg --source followed by sources:
separated by space, like below:
    ```bash
    python -m app.services.ingestion_service --source source1 source2
    ```
5. Run the embedding step to generate embeddings from the articles stored in DB and index them in the ChromaDB
    ```bash
      python -m app.services.embedding_service
   ```
6. Start the application
    ```bash
   uvicorn app.main:app --reload --port 8080
     ```
7. Open the API documentation which includes the list of endpoints at http://localhost:8080/docs

8. Add the LLM environment variables as in the template .env.example. Make sure Ollama is running and the model is 
downloaded. You can check the loaded models here: 
```http://{OLLAMA_BASE_URL}/api/tags```
> **Note:** The application can still run without LLM configuration. In that case the /rag-search would return
> as response the summary of the most relevant article.
## Testing
To run all automated tests 
```bash
  pytest 
```
## Docker setup
1. If running from docker set:
```dotenv
OLLAMA_URL=http://host.docker.internal:11434
```
2. Build the image and start the app container on port 8000
```bash
   docker-compose up --build
```
3. The API Schema can be viewed at http://localhost:8000/docs