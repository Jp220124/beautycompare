import logging
import hashlib
from cachetools import TTLCache
from curl_cffi.requests import AsyncSession
from rapidfuzz import fuzz
from sqlalchemy import select, func

from app.config import get_settings
from app.models.database import async_session, SearchLog

logger = logging.getLogger(__name__)
settings = get_settings()

# Suggestions cache: 30 min TTL, 200 entries
_suggestions_cache: TTLCache = TTLCache(maxsize=200, ttl=1800)

POPULAR_TERMS = [
    "Maybelline Fit Me Foundation",
    "Maybelline Lipstick",
    "Maybelline Mascara",
    "Maybelline Concealer",
    "MAC Ruby Woo",
    "MAC Lipstick",
    "MAC Foundation",
    "MAC Studio Fix",
    "Lakme Kajal",
    "Lakme Lipstick",
    "Lakme Foundation",
    "Lakme Primer",
    "Lakme Compact",
    "L'Oreal Paris Shampoo",
    "L'Oreal Paris Foundation",
    "L'Oreal Paris Serum",
    "Neutrogena Sunscreen",
    "Neutrogena Face Wash",
    "The Ordinary Niacinamide",
    "The Ordinary AHA BHA",
    "The Ordinary Hyaluronic Acid",
    "Minimalist Salicylic Acid",
    "Minimalist Vitamin C",
    "Minimalist Retinol",
    "Nykaa Lipstick",
    "Nykaa Nail Polish",
    "Nykaa Eyeliner",
    "Clinique Moisturizer",
    "Clinique Foundation",
    "Cetaphil Moisturizer",
    "Cetaphil Face Wash",
    "Biotique Shampoo",
    "Forest Essentials",
    "Dove Shampoo",
    "Dove Body Wash",
    "Nivea Body Lotion",
    "Nivea Lip Balm",
    "Vaseline Body Lotion",
    "Garnier Face Wash",
    "Garnier Micellar Water",
    "Himalaya Face Wash",
    "Himalaya Neem Face Pack",
    "Pond's Face Cream",
    "Olay Moisturizer",
    "Olay Serum",
    "Plum Green Tea Face Wash",
    "Plum Body Lotion",
    "Mamaearth Face Wash",
    "Mamaearth Vitamin C Serum",
    "Mamaearth Onion Shampoo",
    "Huda Beauty Lipstick",
    "Huda Beauty Eyeshadow Palette",
    "Charlotte Tilbury Lipstick",
    "Charlotte Tilbury Pillow Talk",
    "Bobbi Brown Foundation",
    "Bobbi Brown Lipstick",
    "Estee Lauder Foundation",
    "Estee Lauder Serum",
    "Kay Beauty Lipstick",
    "Kay Beauty Foundation",
    "Sugar Cosmetics Lipstick",
    "Sugar Cosmetics Eyeliner",
    "Colorbar Lipstick",
    "Colorbar Nail Polish",
    "NYX Lip Liner",
    "NYX Setting Spray",
    "Revlon Lipstick",
    "Revlon Foundation",
    "Innisfree Green Tea",
    "Innisfree Sunscreen",
    "Dot & Key Moisturizer",
    "Dot & Key Sunscreen",
    "Kama Ayurveda",
    "Just Herbs",
    "Tresemme Shampoo",
    "Tresemme Conditioner",
    "Pantene Shampoo",
    "Head & Shoulders Shampoo",
    "WOW Skin Science",
    "mCaffeine Coffee Scrub",
    "mCaffeine Body Wash",
    "Bath & Body Works",
    "Victoria's Secret Mist",
    "Skin Aqua Sunscreen",
    "La Roche Posay Sunscreen",
    "Bioderma Micellar Water",
    "CeraVe Moisturizer",
    "CeraVe Face Wash",
    "Niacinamide Serum",
    "Vitamin C Serum",
    "Retinol Serum",
    "Hyaluronic Acid Serum",
    "Sunscreen SPF 50",
    "Setting Spray",
    "Primer",
    "BB Cream",
    "CC Cream",
    "Compact Powder",
    "Eyeshadow Palette",
    "Blush",
    "Highlighter",
    "Contour Kit",
]

TRENDING = [
    "Maybelline Fit Me Foundation",
    "The Ordinary Niacinamide",
    "MAC Ruby Woo",
    "Lakme Kajal",
    "Vitamin C Serum",
    "Sunscreen SPF 50",
    "Minimalist Salicylic Acid",
    "Charlotte Tilbury Pillow Talk",
]


def _cache_key(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


async def _fetch_nykaa_suggestions(query: str) -> list[str]:
    """Fetch autocomplete suggestions from Nykaa's search API."""
    try:
        async with AsyncSession(impersonate="chrome131") as s:
            resp = await s.get(
                "https://www.nykaa.com/gateway-api/search/elastic/auto-suggest",
                params={"q": query, "searchType": "Manual"},
                timeout=5,
            )
            if resp.status_code != 200:
                logger.debug(f"Nykaa suggestions returned {resp.status_code}")
                return []

            data = resp.json()
            suggestions = []
            # The response typically has a "suggestions" or "categories" field
            for item in data.get("response", {}).get("suggestions", []):
                text = item.get("name") or item.get("text") or ""
                if text:
                    suggestions.append(text)
            # Also check products in the response
            for item in data.get("response", {}).get("products", []):
                name = item.get("name") or item.get("title") or ""
                if name:
                    suggestions.append(name)
            return suggestions[:8]
    except Exception as e:
        logger.debug(f"Nykaa suggestions error: {e}")
        return []


def _match_popular_terms(query: str, limit: int = 8) -> list[str]:
    """Match query against popular beauty terms using prefix, substring, and fuzzy matching."""
    q_lower = query.lower().strip()
    matched_terms = set()
    matches = []

    # Prefix matches (highest priority)
    for term in POPULAR_TERMS:
        if term.lower().startswith(q_lower):
            matches.append((term, 100))
            matched_terms.add(term)

    # Substring / word-prefix matches (e.g. "lip" matches "MAC Lipstick")
    for term in POPULAR_TERMS:
        if term in matched_terms:
            continue
        t_lower = term.lower()
        if q_lower in t_lower:
            matches.append((term, 90))
            matched_terms.add(term)
        else:
            # Check if query matches start of any word in the term
            words = t_lower.split()
            if any(w.startswith(q_lower) for w in words):
                matches.append((term, 85))
                matched_terms.add(term)

    # Fuzzy matches (lower priority)
    for term in POPULAR_TERMS:
        if term in matched_terms:
            continue
        score = fuzz.token_sort_ratio(q_lower, term.lower())
        if score >= 50:
            matches.append((term, score))

    matches.sort(key=lambda x: x[1], reverse=True)
    return [m[0] for m in matches[:limit]]


async def _search_log_suggestions(query: str, limit: int = 5) -> list[str]:
    """Find matching past searches from the search_logs table."""
    try:
        async with async_session() as session:
            q_lower = f"%{query.lower().strip()}%"
            stmt = (
                select(SearchLog.query, func.count(SearchLog.id).label("cnt"))
                .where(func.lower(SearchLog.query).like(q_lower))
                .where(SearchLog.results_count > 0)
                .group_by(func.lower(SearchLog.query))
                .order_by(func.count(SearchLog.id).desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            return [row[0] for row in result.all()]
    except Exception as e:
        logger.debug(f"Search log suggestions error: {e}")
        return []


async def get_suggestions(query: str, limit: int = 8) -> list[str]:
    """Get autocomplete suggestions from multiple sources, combined and deduplicated."""
    query = query.strip()
    if not query:
        return TRENDING[:limit]

    # Check cache
    key = _cache_key(query)
    cached = _suggestions_cache.get(key)
    if cached is not None:
        return cached[:limit]

    # Gather from all sources
    nykaa = await _fetch_nykaa_suggestions(query)
    popular = _match_popular_terms(query, limit)
    log_matches = await _search_log_suggestions(query, limit)

    # Combine with deduplication (case-insensitive)
    seen = set()
    combined = []

    for source in [nykaa, popular, log_matches]:
        for item in source:
            normalized = item.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                combined.append(item.strip())
            if len(combined) >= limit:
                break
        if len(combined) >= limit:
            break

    # Cache the result
    _suggestions_cache[key] = combined

    return combined[:limit]


def get_trending() -> list[str]:
    """Return trending search terms."""
    return list(TRENDING)
