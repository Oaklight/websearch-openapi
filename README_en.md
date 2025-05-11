# websearch-openapi-mcp

[中文](README_zh.md) | [English](README_en.md)

## Start the Server via Python

```bash
python main.py --port 8000 --host 0.0.0.0 --mode <openapi|mcp>
```

This will start the OpenAPI or MCP server on <http://0.0.0.0:8000>.

The default MCP mode is Streamable HTTP, URL is <http://0.0.0.0:8000/mcp>.

For SSE mode, add `--mcp-mode sse`, URL is <http://0.0.0.0:8000/sse>.

## Start the Server via Docker

```bash
docker run -p 8000:8000 \
    --name websearch-openapi-server \
   -e API_BEARER_TOKEN="your_token_here" \
   -e SEARXNG_BASE_URL="https://searxng.url" \
   oaklight/websearch-openapi-server:latest
```

or using docker compose:

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

The server can be configured with the following environment variables:

1. **`API_BEARER_TOKEN`**:
   This token is used for securing API endpoints. If set, it enables authentication for all protected routes using Bearer Token verification. Requests must include an `Authorization` header with the format: `Bearer <your_token>`.

   **Behavior**:

   - When set, `verify_token` enforces token validation.
   - When unset or empty, `verify_token` allows all requests without authentication (useful for testing, or MCP mode where per-request authorization headers are unavailable).

   **Configuration recommendation**:

   - For API mode (`openapi`): Set `API_BEARER_TOKEN` for production to secure endpoints
   - For MCP mode (`mcp`): Typically runs without authentication (`API_BEARER_TOKEN` unset)

   Example configuration with Docker:

   ```bash
   -e API_BEARER_TOKEN="my_secure_token"
   ```

2. **`SEARXNG_BASE_URL`**:
   The base URL for SearXNG, a privacy-respecting metasearch engine. This is required for enabling functionality at `/search_searxng`.

   **Behavior**:

   - If set, the `WebSearchSearxng` tool uses this URL to perform queries.
   - If unset or empty, the `/search_searxng` endpoint will be **disabled** (i.e., requests to this endpoint will raise an error) with a `503 Service Unavailable` status code. The error will explicitly state that the SearXNG search feature is not configured and suggest setting the `SEARXNG_BASE_URL`.

   **Configuration recommendation**:

   - For API mode (`openapi`): Ensure proper configuration of `SEARXNG_BASE_URL`
   - For MCP mode (`mcp`): SearXNG can be optionally configured based on needs

   Example configuration with Docker:

   ```bash
   -e SEARXNG_BASE_URL="https://searxng.instance.com"
   ```

Ensure environment variables are configured based on the server mode:

- **API Mode (`openapi`)**: It is recommended to set `API_BEARER_TOKEN` for production to secure endpoints and ensure proper configuration for `SEARXNG_BASE_URL`.
- **MCP Mode (`mcp`)**: Integration scenarios often run without authentication (`API_BEARER_TOKEN` unset), and SearXNG may optionally be configured depending on the need.
