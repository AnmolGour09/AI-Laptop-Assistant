import asyncio
import logging
import os
import requests
from datetime import datetime
from typing import Any

from ddgs import DDGS
from dotenv import load_dotenv
from livekit.agents import function_tool

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _format_results(items: list[dict[str, Any]], *, limit: int) -> str:
    formatted = []
    for item in items[:limit]:
        title = item.get("title") or "No title"
        link = item.get("link") or item.get("href") or ""
        snippet = item.get("snippet") or item.get("body") or ""
        if not link:
            continue
        formatted.append(f"{len(formatted) + 1}. {title}\n{link}\n{snippet}".strip())
    return "\n\n".join(formatted)


def _google_search(
    query: str,
    api_key: str,
    search_engine_id: str,
) -> tuple[list[dict[str, Any]], str | None]:
    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": api_key,
                "cx": search_engine_id,
                "q": query,
                "num": 5,
            },
            timeout=(3.05, 8),
        )
    except requests.RequestException as error:
        logger.warning("Google Search request failed: %s", type(error).__name__)
        return [], "request failed"

    try:
        data = response.json()
    except ValueError:
        logger.warning("Google Search returned a non-JSON response (HTTP %s)", response.status_code)
        return [], f"HTTP {response.status_code}"

    if response.status_code != 200:
        errors = data.get("error", {}).get("errors", [])
        reason = errors[0].get("reason", "request failed") if errors else "request failed"
        logger.warning("Google Search failed: HTTP %s (%s)", response.status_code, reason)
        return [], reason

    return data.get("items", []), None


def _duckduckgo_search(query: str) -> list[dict[str, Any]]:
    with DDGS(timeout=10) as search:
        return search.text(query, max_results=5) or []


@function_tool
async def google_search(query: str) -> str:
    query = query.strip()
    if not query:
        return "Search needs a non-empty query. Please say what you want me to find."

    api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_engine_id = os.getenv("SEARCH_ENGINE_ID")
    google_error = "not configured"

    if api_key and search_engine_id:
        google_results, google_error = await asyncio.to_thread(
            _google_search,
            query,
            api_key,
            search_engine_id,
        )
        formatted = _format_results(google_results, limit=5)
        if formatted:
            logger.info("Google Search returned %s result(s)", len(google_results))
            return formatted

    logger.info("Trying DuckDuckGo search fallback")
    try:
        fallback_results = await asyncio.to_thread(_duckduckgo_search, query)
    except Exception as error:
        logger.exception("DuckDuckGo search fallback failed")
        fallback_error = type(error).__name__
    else:
        formatted = _format_results(fallback_results, limit=5)
        if formatted:
            logger.info("DuckDuckGo returned %s result(s)", len(fallback_results))
            return formatted
        fallback_error = "no results"

    logger.error(
        "All search providers failed (Google: %s; DuckDuckGo: %s)",
        google_error,
        fallback_error,
    )
    if google_error == "accessNotConfigured":
        return (
            "Google Custom Search is disabled for this Google Cloud project, and the backup "
            "search returned no results. Enable the Custom Search API in Google Cloud or try "
            "your search again later."
        )
    return "Search is temporarily unavailable from both Google and DuckDuckGo. Please try again in a moment."

@function_tool
async def get_current_datetime() -> str:
    return datetime.now().isoformat()
