import httpx
from app.core.config import settings
from app.core.cache import search_cache


def search(query: str, max_results: int = 5) -> list[dict]:
    cached = search_cache.get(query)
    if cached:
        return cached

    if settings.mock_mode or not settings.tavily_api_key:
        results = [
            {"title": f"Local market context for: {query}", "url": "https://example.com/market-context", "content": "No live web search configured, using placeholder context."}
        ]
        search_cache.set(query, results)
        return results

    response = httpx.post(
        "https://api.tavily.com/search",
        json={"api_key": settings.tavily_api_key, "query": query, "max_results": max_results},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    results = [{"title": r.get("title"), "url": r.get("url"), "content": r.get("content")} for r in data.get("results", [])]
    search_cache.set(query, results)
    return results
