import asyncio
import logging
import time

from app.adapters.base import BaseAdapter
from app.adapters.nykaa import NykaaAdapter
from app.adapters.amazon import AmazonAdapter
from app.adapters.tira import TiraAdapter
from app.models.schemas import SearchResponse, Platform
from app.services.matcher import match_products
from app.services import cache
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize adapters
ADAPTERS: list[BaseAdapter] = [
    NykaaAdapter(),
    AmazonAdapter(),
    TiraAdapter(),
]


async def search_products(query: str, limit: int = 10) -> SearchResponse:
    """
    Search for products across all platforms.

    1. Check cache
    2. Fire parallel requests to all adapters
    3. Match products across platforms
    4. Cache and return results
    """
    # 1. Check cache
    cached = cache.get_cached(query)
    if cached:
        cached.cached = True
        return cached

    start_time = time.time()

    # 2. Fire parallel searches
    platforms_searched: list[str] = []
    platforms_failed: list[str] = []
    all_results: dict[str, list] = {}

    async def _search_adapter(adapter: BaseAdapter):
        try:
            results = await asyncio.wait_for(
                adapter.search(query, limit=limit),
                timeout=settings.request_timeout,
            )
            all_results[adapter.platform.value] = results
            platforms_searched.append(adapter.platform.value)
            logger.info(
                f"{adapter.platform_name}: found {len(results)} results for '{query}'"
            )
        except asyncio.TimeoutError:
            logger.error(f"{adapter.platform_name}: timed out")
            platforms_failed.append(adapter.platform.value)
        except Exception as e:
            logger.error(f"{adapter.platform_name}: failed - {e}")
            platforms_failed.append(adapter.platform.value)

    # Run all adapters concurrently
    await asyncio.gather(*[_search_adapter(a) for a in ADAPTERS])

    # 3. Match products across platforms
    matched = match_products(all_results)

    elapsed_ms = int((time.time() - start_time) * 1000)

    # 4. Build response
    response = SearchResponse(
        query=query,
        results=matched,
        total_results=len(matched),
        platforms_searched=platforms_searched,
        platforms_failed=platforms_failed,
        cached=False,
        search_time_ms=elapsed_ms,
    )

    # 5. Cache results (only if at least one platform succeeded)
    if platforms_searched:
        cache.set_cached(query, response)

    return response
