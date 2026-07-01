"""Tavily web search provider."""
import httpx
from typing import TYPE_CHECKING
from .base import WebSearchProvider, SearchResult

if TYPE_CHECKING:
    from mybot.utils.config import Config


class TavilySearchProvider(WebSearchProvider):
    def __init__(self, config: "Config") -> None:
        self.api_key = config.websearch.api_key

    async def search(self, query: str) -> list[SearchResult]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={"query": query, "max_results": 5},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            response.raise_for_status()
            data = response.json()
            return [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", ""),
                )
                for r in data.get("results", [])
            ]
