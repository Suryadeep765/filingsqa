# FilingsQA: Kafka and Docker

This extension adds a small asynchronous ingestion queue to FilingsQA.

## Architecture

- FastAPI exposes `POST /ingest` and publishes an ingestion event.
- Kafka stores the event in the `filing-ingestion` topic.
- A separate worker consumes the event and runs the existing SEC fetch, clean, chunk, embed, and FAISS indexing scripts.
- The existing `/search` and `/ask` routes remain synchronous and unchanged in behavior.

## Run locally with Docker Compose

1. Copy `.env.example` to `.env`.
2. Set `SEC_USER_AGENT` to a valid SEC identity string.
3. Ensure Ollama is running on the host and the configured model is available.
4. Build and start the services:

```powershell
docker compose up --build
```

5. Open the API docs at http://localhost:8000/docs.
6. Queue an ingestion job:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/ingest -ContentType "application/json" -Body '{"limit": 10}'
```

7. Check worker logs:

```powershell
docker compose logs -f worker
```

8. Check API health:

```powershell
Invoke-RestMethod http://localhost:8000/health
```

## Important notes

- The API, Kafka broker, and ingestion worker run as separate containers.
- The worker uses the existing sequential ingestion scripts. Their output files are shared, so this simple implementation processes jobs sequentially; do not scale the worker horizontally yet.
- The API and worker mount `./data` so both can see the FAISS index and metadata. Keep the data files local; they are not committed to the repository.
- Ollama remains a host service in this setup, so the API container uses `host.docker.internal` to reach it.
- The first build downloads Python dependencies. The first ingestion run also downloads the embedding model.
- For a production system, add durable job status storage, idempotent job handling, dead-letter handling, and a shared object store or database for index artifacts.
