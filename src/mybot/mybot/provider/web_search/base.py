"""Base class for web search providers."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from mybot.utils.config import Config


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class WebSearchProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> list[SearchResult]:
        pass

    @staticmethod
    def from_config(config: "Config") -> "WebSearchProvider":
        if config.websearch is None:
            raise ValueError("Websearch not configured")

        match config.websearch.provider:
            case "brave":
                from .brave import BraveSearchProvider
                return BraveSearchProvider(config)
            case "tavily":
                from .tavily import TavilySearchProvider
                return TavilySearchProvider(config)
            case _:
                raise ValueError(f"Unknown websearch provider: {config.websearch.provider}")