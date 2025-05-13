import os
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastmcp import FastMCP
from toolregistry.hub import Calculator, WebSearchGoogle, WebSearchSearxng
from toolregistry.hub.websearch import WebSearchGeneral

load_dotenv()

# ======== initialize tools ========
websearch_google = WebSearchGoogle()
websearch_searxng = WebSearchSearxng(searxng_base_url=os.getenv("SEARXNG_BASE_URL"))
calculator = Calculator()
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


token_required = bool(os.getenv("API_BEARER_TOKEN"))
security_dependency = [] if not token_required else [Depends(verify_token)]


# ======== Define FastAPI app ========
app = FastAPI(
    title="Tool Registry OpenAPI Server",
    description="An API for accessing various tools like calculators, unit converters, and web search engines.",
    version="0.2.0",
)


@app.post(
    "/calc_help",
    summary="Get help with calculator functions",
    description=calculator.help.__doc__,
    dependencies=security_dependency,
    operation_id="calc_help",
)
def calc_help(fn_name: str) -> str:
    """Get help with calculator functions."""
    try:
        return calculator.help(fn_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid function name: {str(e)}",
        ) from e


@app.post(
    "/calc_allowed_fns",
    summary="Get allowed functions for calculator",
    description=calculator.allowed_fns_in_evaluate.__doc__,
    dependencies=security_dependency,
    operation_id="calc_allowed_fns",
)
def calc_allowed_fns() -> List[str]:
    """Get allowed functions for calculator."""
    return calculator.allowed_fns_in_evaluate()


@app.post(
    "/calc_evaluate",
    summary="Evaluate a mathematical expression",
    description=calculator.evaluate.__doc__.replace(
        "This method is intended for complex expressions that combine two or more operations or advanced mathematical functions.",
        "",
    )
    .replace(
        "For simple, single-step operations, please directly use the corresponding static method (e.g., add, subtract).",
        "",
    )
    .replace("allowed_fns_in_evaluate()", "calc_allowed_fns")
    .replace("help", "calc_help"),
    dependencies=security_dependency,
    operation_id="calc_evaluate",
)
def calc_evaluate(expression: str) -> Union[float, int, bool]:
    """Evaluates a mathematical expression using a unified interface."""
    try:
        return calculator.evaluate(expression)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid expression: {str(e)}",
        ) from e


@app.post(
    "/search_google",
    summary="Search Google for a query",
    description=websearch_google.search.__doc__,
    dependencies=security_dependency,
    operation_id="search_google",
)
def search_google(
    query: str,
    number_results: int = 5,
    timeout: Optional[float] = None,
) -> List[Dict[str, str]]:
    """Perform search and return results."""
    results = websearch_google.search(
        query,
        number_results=number_results,
        timeout=timeout,
    )
    return results


@app.post(
    "/search_searxng",
    summary="Search SearXNG for a query",
    description=websearch_searxng.search.__doc__,
    dependencies=security_dependency,
    operation_id="search_searxng",
)
def search_searxng(
    query: str,
    number_results: int = 5,
    timeout: Optional[float] = None,
) -> List[Dict[str, str]]:
    """Perform search and return results."""
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
    description=WebSearchGeneral.extract.__doc__,
    dependencies=security_dependency,
    operation_id="extract_webpage",
)
def extract_webpage(url: str, timeout: Optional[float] = None) -> str:
    """Extract content from a given URL using available methods."""
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
