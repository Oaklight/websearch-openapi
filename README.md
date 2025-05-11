# Tool Registry API

## Start the Server via Uvicorn

```bash
uvicorn main:app --reload --port 8000 --host 0.0.0.0
```

This will start the server on the default port (<http://127.0.0.1:8000>).

## Start the Server via Docker

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

## Explore the API

Once the server is running, visit the following URLs:

1. **Interactive API Documentation (Swagger UI)**
   Open your browser and go to:
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

2. **Alternative API Documentation (ReDoc)**
   View the ReDoc documentation at:
   [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## MCP / OpenAPI Mode Switch

The server supports running in multiple modes, configurable via command-line arguments:

- **OpenAPI Mode (default)**:

  ```yaml
  command: ["python", "main.py", "--host=0.0.0.0", "--port=8000", "--mode=openapi"]
  ```

- **MCP Streamable HTTP Mode**:

  ```yaml
  command: ["python", "main.py", "--host=0.0.0.0", "--port=8000", "--mode=mcp"]
  ```

- **MCP SSE Mode**:

  ```yaml
  command: ["python", "main.py", "--host=0.0.0.0", "--port=8000", "--mode=mcp", "--mcp-mode=sse"]
  ```

## Environment Variable Configuration

To configure the server, you can provide the following environment variables:

1. **`API_BEARER_TOKEN`**:  
   This token is used for securing API endpoints. If set, it enables authentication for all protected routes using Bearer Token verification. Requests must include an `Authorization` header with the format: `Bearer <your_token>`.  
   **Behavior**:  
   - When set, `verify_token` enforces token validation.  
   - When unset or empty, `verify_token` allows all requests without authentication (useful for testing, or MCP mode where per-request authorization headers are unavailable).

   Example configuration with Docker:

   ```bash
   -e API_BEARER_TOKEN="my_secure_token"
   ```

2. **`SEARXNG_BASE_URL`**:  
   The base URL for SearXNG, a privacy-respecting metasearch engine. This is required for enabling functionality at `/search_searxng`.  
   **Behavior**:  
   - If set, the `WebSearchSearxng` tool uses this URL to perform queries.  
   - If unset or empty, the `/search_searxng` endpoint will be **disabled** (i.e., requests to this endpoint will raise an error) with a `503 Service Unavailable` status code. The error will explicitly state that the SearXNG search feature is not configured and suggest setting the `SEARXNG_BASE_URL`.

   Example configuration with Docker:

   ```bash
   -e SEARXNG_BASE_URL="https://searxng.instance.com"
   ```

Ensure environment variables are configured based on the server mode:

- **API Mode (`openapi`)**: It is recommended to set `API_BEARER_TOKEN` for production to secure endpoints and ensure proper configuration for `SEARXNG_BASE_URL`.
- **MCP Mode (`mcp`)**: Integration scenarios often run without authentication (`API_BEARER_TOKEN` unset), and SearXNG may optionally be configured depending on the need.
