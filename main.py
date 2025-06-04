import os
import textwrap
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from toolregistry.hub import Calculator, WebSearchGoogle, WebSearchSearXNG
from toolregistry.hub.websearch import Fetch


class CalcEvaluateRequest(BaseModel):
    expression: str = Field(
        ...,
        description="Mathematical expression to evaluate",
        example="26 * 9 / 5 + 32",
    )

class CalcListAllowedFnsRequest(BaseModel):
    with_help: bool = Field(
        False, description="Include help messages for each function"
    )

class CalcHelpRequest(BaseModel):
    fn_name: str = Field(
        ..., description="Function name to get help for", example="sin"
    )


class WebSearchRequest(BaseModel):
    query: str = Field(
        ..., description="Search query string", example="weather in Beijing"
    )
    number_results: int = Field(
        5, description="Number of results to return", ge=1, le=20
    )
    timeout: Optional[float] = Field(None, description="Timeout in seconds")


class WebFetchWebpageRequest(BaseModel):
    url: str = Field(
        ..., description="URL of webpage to extract", example="https://example.com"
    )
    timeout: Optional[float] = Field(None, description="Timeout in seconds")


load_dotenv()

# ======== initialize tools ========
websearch_google = WebSearchGoogle()
websearch_searxng = WebSearchSearXNG(searxng_base_url=os.getenv("SEARXNG_BASE_URL"))
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
    "/calc-help",
    summary="Get help with calculator functions",
    dependencies=security_dependency,
    operation_id="calc-help",
)
def calc_help(data: CalcHelpRequest) -> str:
    """Get help with calculator functions."""
    try:
        return calculator.help(data.fn_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid function name: {str(e)}",
        ) from e


@app.post(
    "/calc-list_allowed_fns",
    summary="Get allowed functions for calc_evaluate",
    description=calculator.list_allowed_fns.__doc__,
    dependencies=security_dependency,
    operation_id="calc-list_allowed_fns",
)
def calc_list_allowed_fns(data: CalcListAllowedFnsRequest) -> str:
    """Get allowed functions for calculator."""
    return calculator.list_allowed_fns(data.with_help)


@app.post(
    "/calc-evaluate",
    summary="Evaluate a mathematical expression",
    description=textwrap.dedent(
        """Evaluates a mathematical expression.

        The `expression` can use named functions like `add(2, 3)` or native operators like `2 + 3`. Pay attention to operator precedence and use parentheses to ensure the intended order of operations. For example: `"add(2, 3) * pow(2, 3) + sqrt(16)"` or `"(2 + 3) * (2 ** 3) + sqrt(16)"` or mixed.

        - Use `calc-list_allowed_fns()` to view available functions. Set `with_help` to `True` to include function signatures and docstrings.
        - Use `calc-help` for detailed information on specific functions.

        **Note**: If an error occurs due to an invalid expression, query the `help` method to check the function usage and ensure it is listed by `calc-list_allowed_fns()`.
        """
    ),
    dependencies=security_dependency,
    operation_id="calc-evaluate",
)
def calc_evaluate(data: CalcEvaluateRequest) -> Union[float, int, bool]:
    expression = data.expression.strip()  # Remove leading/trailing whitespace
    if not expression:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expression cannot be empty.",
        )
    try:
        return calculator.evaluate(expression)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid expression: {str(e)}",
        ) from e


@app.post(
    "/web-search_google",
    summary="Search Google for a query",
    description=websearch_google.search.__doc__
    + "\n Note: when used, properly cited results' URLs at the end of the generated content, unless instructed otherwise."
    + "\nIncrease the `number_results` in case of deep research.",
    dependencies=security_dependency,
    operation_id="web-search_google",
)
def search_google(data: WebSearchRequest) -> List[Dict[str, str]]:
    results = websearch_google.search(
        data.query,
        number_results=data.number_results,
        timeout=data.timeout,
    )
    return results


@app.post(
    "/web-search_searxng",
    summary="Search SearXNG for a query",
    description=websearch_searxng.search.__doc__
    + "\n Note: when used, properly cited results' URLs at the end of the generated content, unless instructed otherwise."
    + "\nIncrease the `number_results` in case of deep research.",
    dependencies=security_dependency,
    operation_id="web-search_searxng",
)
def search_searxng(data: WebSearchRequest) -> List[Dict[str, str]]:
    if not os.getenv("SEARXNG_BASE_URL"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SearXNG search feature is not configured. Please set the SEARXNG_BASE_URL environment variable.",
        )

    results = websearch_searxng.search(
        data.query,
        number_results=data.number_results,
        timeout=data.timeout,
    )
    return results


@app.post(
    "/web-fetch_webpage",
    summary="Extract content from a webpage",
    description=Fetch.fetch_content.__doc__,
    dependencies=security_dependency,
    operation_id="web-fetch_webpage",
)
def fetch_webpage(data: WebFetchWebpageRequest) -> str:
    content = Fetch.fetch_content(data.url, timeout=data.timeout)
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
