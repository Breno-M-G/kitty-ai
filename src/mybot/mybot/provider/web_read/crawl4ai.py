"""Crawl4AI provider for web page reading."""
import sys
if sys.platform == 'win32':
    import ctypes
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from crawl4ai import AsyncWebCrawler
from .base import WebReadProvider, ReadResult

class Crawl4AIProvider(WebReadProvider):
    """Web read provider using Crawl4AI."""

    def __init__(self):
        """Initialize Crawl4AI provider."""
        pass

    async def read(self, url: str) -> ReadResult:
        """Read a web page using Crawl4AI."""
        try:
            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url)
                if not result.success:
                    raise Exception(result.error_message or "Failed to crawl page")
                content = (result.markdown or "").encode('utf-8', errors='replace').decode('utf-8')
                title = (result.metadata.get("title", "") if result.metadata else "").encode('utf-8', errors='replace').decode('utf-8')
                return ReadResult(
                    url=url,
                    title=title,
                    content=content,
                    error=None,
                )
        except Exception as e:
            return ReadResult(
                url=url,
                title="",
                content="",
                error=str(e),
            )
