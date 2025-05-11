# websearch-openapi-mcp

[English](README_en.md) | [中文](README_zh.md)

## 使用 Python 启动服务器

```bash
python main.py --port 8000 --host 0.0.0.0 --mode <openapi|mcp>
```

这将启动 OpenAPI 或 MCP 服务器 <http://0.0.0.0:8000>。

MCP 默认模式为 Streamable HTTP, URL 为<http://0.0.0.0:8000/mcp>。

SSE 模式需要添加 `--mcp-mode sse`，对应 URL 为<http://0.0.0.0:8000/sse>。

## 使用 Docker 启动服务器

```bash
docker run -p 8000:8000 \
    --name websearch-openapi-server \
   -e API_BEARER_TOKEN="your_token_here" \
   -e SEARXNG_BASE_URL="https://searxng.url" \
   oaklight/websearch-openapi-server:latest
```

或者使用 docker compose 启动：

```bash
docker compose up -d
```

## 浏览 API

服务器启动后，OpenAPI模式下可以访问以下 URL：

1. **交互式 API 文档 (Swagger UI)**
   打开浏览器并访问：
   [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

2. **备用 API 文档 (ReDoc)**
   查看 ReDoc 文档：
   [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## MCP / OpenAPI 模式切换

服务器支持多种运行模式，可通过命令行参数进行配置：

- **OpenAPI 模式（默认）**：

  ```yaml
  command: ["python", "main.py", "--host=0.0.0.0", "--port=8000", "--mode=openapi"]
  ```

- **MCP 可流式 HTTP 模式**：

  ```yaml
  command: ["python", "main.py", "--host=0.0.0.0", "--port=8000", "--mode=mcp"]
  ```

- **MCP SSE 模式**：

  ```yaml
  command: ["python", "main.py", "--host=0.0.0.0", "--port=8000", "--mode=mcp", "--mcp-mode=sse"]
  ```

## 环境变量配置

可通过以下环境变量来配置服务器：

1. **`API_BEARER_TOKEN`**：
   此令牌用于保护 API 端点。如果设置了该令牌，则所有受保护的路由将启用基于 Bearer Token 的验证。请求必须包含以下格式的 `Authorization` 请求头：`Bearer <your_token>`。

   **行为**：

   - 如果设置，`verify_token` 强制执行令牌验证。
   - 如果未设置或为空，`verify_token` 将允许未验证的所有请求（适用于测试，或 MCP 模式下无法提供每个请求的认证头）。

   **使用 Docker 配置示例**：

   ```bash
   -e API_BEARER_TOKEN="my_secure_token"
   ```

2. **`SEARXNG_BASE_URL`**：
   基于隐私保护的元搜索引擎 SearXNG 的基础 URL。这是启用 `/search_searxng` 功能所必需的。

   **行为**：

   - 如果设置，`WebSearchSearxng` 工具将使用该 URL 执行查询。
   - 如果未设置或为空，`/search_searxng` 端点将被**禁用**（对该端点的请求将引发错误），并返回 `503 Service Unavailable` 状态码。错误消息将明确指出 SearXNG 搜索功能未配置，并建议设置 `SEARXNG_BASE_URL`。

   **使用 Docker 配置示例**：

   ```bash
   -e SEARXNG_BASE_URL="https://searxng.instance.com"
   ```

根据服务器模式配置环境变量：

- **API 模式 (`openapi`)**：建议在生产环境中设置 `API_BEARER_TOKEN` 以保护端点，并正确配置 `SEARXNG_BASE_URL`。
- **MCP 模式 (`mcp`)**：集成场景通常在未设置 `API_BEARER_TOKEN` 的情况下运行，并且根据需要确定 SearXNG 配置是否可选。

```
