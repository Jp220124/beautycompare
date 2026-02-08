from fastapi import APIRouter, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.schemas import SearchResponse
from app.services.search import search_products
from app.services.cache import get_cache_stats
from app.services.suggestions import get_suggestions, get_trending

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
@limiter.limit("10/minute")
async def search(
    request: Request,
    q: str = Query(..., min_length=2, max_length=200, description="Search query"),
    limit: int = Query(10, ge=1, le=30, description="Max results per platform"),
):
    """Search for beauty products across Nykaa, Tira, and Amazon India."""
    response = await search_products(query=q, limit=limit)
    return response


@router.get("/suggestions")
@limiter.limit("30/minute")
async def suggestions(
    request: Request,
    q: str = Query("", max_length=200, description="Partial search query"),
):
    """Return autocomplete suggestions for a partial query."""
    if not q.strip():
        return {"suggestions": get_trending()}
    results = await get_suggestions(query=q)
    return {"suggestions": results}


@router.get("/platforms")
async def get_platforms():
    """List all supported platforms."""
    return {
        "platforms": [
            {"id": "nykaa", "name": "Nykaa", "color": "#FC2779", "url": "https://www.nykaa.com"},
            {"id": "amazon", "name": "Amazon India", "color": "#FF9900", "url": "https://www.amazon.in"},
            {"id": "tira", "name": "Tira Beauty", "color": "#000000", "url": "https://www.tirabeauty.com"},
        ]
    }


@router.get("/cache-stats")
async def cache_stats():
    """Return cache statistics."""
    return get_cache_stats()
