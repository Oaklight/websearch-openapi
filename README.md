# Tool Registry API

### Start the Server via Uvicorn

```bash
uvicorn main:app --reload --port 8000 --host 0.0.0.0
```

This will start the server on the default port (<http://127.0.0.1:8000>).

### Start the Server via Docker

```bash
docker run -p 8000:8000 \
    --name websearch-openapi-server \
   -e API_BEARER_TOKEN="your_token_here" \
   -e SEARXNG_BASE_URL="https://searxng.url" \
   oaklight/websearch-openapi-server:latest
```

or by docker compose:

```bash
docker compose up -d
```

### Explore the API

Once the server is running, visit the following URLs:

1. **Interactive API Documentation (Swagger UI)**
   Open your browser and go to:
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

2. **Alternative API Documentation (ReDoc)**
   View the ReDoc documentation at:
   [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
