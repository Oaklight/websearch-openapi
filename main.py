import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
    if credentials.credentials != valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
        )


# ======== Define FastAPI app ========
app = FastAPI(
    title="Tool Registry API",
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
    dependencies=[Depends(verify_token)],
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
