import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastmcp import FastMCP
from toolregistry.hub import (
    WebSearchGoogle,
    WebSearchSearxng,
)
from toolregistry.hub.websearch import WebSearchGeneral

load_dotenv()

# ======== initialize tools ========
websearch_google = WebSearchGoogle()
websearch_searxng = WebSearchSearxng(searxng_base_url=os.getenv("SEARXNG_BASE_URL"))

# ======== Define security ========
# Define the token authentication scheme
security = HTTPBearer()


# Function to verify the Bearer Token
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    valid_token = os.getenv(
        "API_BEARER_TOKEN"
    )  # Store your token in an environment variable for safety
    if not valid_token:  # If the token is empty or not set, disable verification
        return
    if credentials.credentials != valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
        )


# ======== Define FastAPI app ========
app = FastAPI(
    title="Tool Registry OpenAPI Server",
    description="An API for accessing various tools like calculators, unit converters, and web search engines.",
    version="0.1.0",
)


@app.post(
    "/search_google",
    summary="Search Google for a query",
    dependencies=[Depends(verify_token)],
)
def search_google(
    query: str,
    number_results: int = 5,
    timeout: Optional[float] = None,
) -> List[Dict[str, str]]:
    """Perform search and return results.

    Args:
        query: The search query.
        number_results: The maximum number of results to return. Default is 5.
        timeout: Optional timeout override in seconds.

    Returns:
        List of search results, each containing:
            - 'title': The title of the search result
            - 'url': The URL of the search result
            - 'content': The description/content from Google
            - 'excerpt': Same as content (for compatibility with WebSearchSearxng)
    """
    results = websearch_google.search(
        query,
        number_results=number_results,
        timeout=timeout,
    )
    return results


@app.post(
    "/search_searxng",
    summary="Search SearXNG for a query",
    dependencies=[Depends(verify_token)],  # Enabled dependency
)
def search_searxng(
    query: str,
    number_results: int = 5,
    timeout: Optional[float] = None,
) -> List[Dict[str, str]]:
    """Perform search and return results.

    Args:
        query: The search query.
        number_results: The maximum number of results to return. Default is 5.
        timeout: Optional timeout override in seconds.

    Returns:
        List of search results, each containing:
            - 'title': The title of the search result
            - 'url': The URL of the search result
            - 'content': The description/content from searxng
            - 'excerpt': Same as content (for compatibility with WebSearchSearxng)
    """
    if not os.getenv("SEARXNG_BASE_URL"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SearXNG search feature is not configured. Please set the SEARXNG_BASE_URL environment variable.",
        )

    results = websearch_searxng.search(
        query,
        number_results=number_results,
        timeout=timeout,
    )
    return results


@app.post(
    "/extract_webpage",
    summary="Extract content from a webpage",
    dependencies=[Depends(verify_token)],
)
def extract_webpage(url: str, timeout: Optional[float] = None) -> str:
    """Extract content from a given URL using available methods.

    Args:
        url (str): The URL to extract content from.
        timeout (float, optional): Request timeout in seconds. Defaults to TIMEOUT_DEFAULT (10). Usually not needed.

    Returns:
        str: Extracted content from the URL, or empty string if extraction fails.
    """
    content = WebSearchGeneral.extract(url, timeout=timeout)
    return content


# ======== FastMCP server ========

mcp = FastMCP.from_fastapi(app, name="Tool Registry MCP Server")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Tool Registry API server.")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to. Default is 0.0.0.0.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to. Default is 8000.",
    )
    parser.add_argument(
        "--mode",
        choices=["openapi", "mcp"],
        default="openapi",
        help="Server mode: openapi or mcp. Default is openapi.",
    )
    parser.add_argument(
        "--mcp-mode",
        choices=["streamable-http", "sse", "stdio"],
        default="streamable-http",
        help="MCP transport mode for mcp mode. Default is streamable-http.",
    )
    args = parser.parse_args()

    if args.mode == "openapi":
        import uvicorn

        uvicorn.run(app, host=args.host, port=args.port)
    elif args.mode == "mcp":
        if args.mcp_mode == "stdio":
            mcp.run()  # Run MCP in stdio mode; assumes FastMCP supports this method
        else:
            mcp.run(transport=args.mcp_mode, host=args.host, port=args.port)
