import logging
import re
import json

from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession

from app.adapters.base import BaseAdapter
from app.models.schemas import ProductResult, Platform
from app.config import get_settings
from app.utils.text import clean_price, extract_brand, compute_discount

logger = logging.getLogger(__name__)
settings = get_settings()


class NykaaAdapter(BaseAdapter):
    """Adapter for Nykaa using HTML scraping with curl_cffi to bypass Cloudflare."""

    SEARCH_URL = "https://www.nykaa.com/search/result/"

    @property
    def platform(self) -> Platform:
        return Platform.NYKAA

    @property
    def platform_name(self) -> str:
        return "Nykaa"

    @property
    def base_url(self) -> str:
        return "https://www.nykaa.com"

    async def search(self, query: str, limit: int = 10) -> list[ProductResult]:
        """Search Nykaa by scraping the search results page and extracting __PRELOADED_STATE__."""
        try:
            async with AsyncSession(impersonate="chrome131") as s:
                resp = await s.get(
                    self.SEARCH_URL,
                    params={"q": query, "root": "search", "searchType": "Manual"},
                    timeout=settings.request_timeout,
                )
                if resp.status_code != 200:
                    logger.warning(f"Nykaa returned {resp.status_code}")
                    return []

                return self._parse_search_page(resp.text, limit)

        except Exception as e:
            logger.error(f"Nykaa: unexpected error: {e}")
            return []

    def _parse_search_page(self, html: str, limit: int) -> list[ProductResult]:
        """Extract products from Nykaa's window.__PRELOADED_STATE__ JSON."""
        results: list[ProductResult] = []
        soup = BeautifulSoup(html, "lxml")

        for script in soup.find_all("script"):
            text = script.string or ""
            if "window.__PRELOADED_STATE__" not in text:
                continue

            match = re.search(
                r"window\.__PRELOADED_STATE__\s*=\s*({.*})",
                text,
                re.DOTALL,
            )
            if not match:
                continue

            try:
                data = json.loads(match.group(1).rstrip(";"))
            except json.JSONDecodeError:
                logger.warning("Nykaa: failed to parse __PRELOADED_STATE__ JSON")
                continue

            # Search results use searchListingPage, category pages use categoryListing
            products = (
                data.get("searchListingPage", {})
                .get("listingData", {})
                .get("products", [])
            ) or (
                data.get("categoryListing", {})
                .get("listingData", {})
                .get("products", [])
            )

            if not products:
                logger.debug("Nykaa: no products in __PRELOADED_STATE__")
                continue

            for item in products[:limit]:
                try:
                    result = self._parse_product(item)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Nykaa: failed to parse product: {e}")
                    continue

            if results:
                return results

        return results

    def _parse_product(self, item: dict) -> ProductResult | None:
        name = item.get("name") or item.get("title") or ""
        if not name:
            return None

        price = clean_price(
            item.get("price")
            or item.get("offer_price")
            or item.get("final_price")
            or 0
        )
        mrp = clean_price(item.get("mrp") or 0)
        if price <= 0:
            return None

        discount = compute_discount(price, mrp)

        image_url = item.get("imageUrl") or item.get("image_url") or ""
        if image_url and not image_url.startswith("http"):
            image_url = f"https://images-static.nykaa.com/media/catalog/product/{image_url}"

        slug = item.get("slug") or item.get("url_key") or ""
        product_url = f"https://www.nykaa.com/{slug}" if slug else ""

        rating = 0.0
        try:
            rating = float(item.get("rating") or item.get("ratings") or 0)
        except (ValueError, TypeError):
            pass

        rating_count = 0
        try:
            rating_count = int(
                item.get("review_count") or item.get("rating_count") or 0
            )
        except (ValueError, TypeError):
            pass

        brand_raw = item.get("brandName") or item.get("brand_name") or item.get("brand") or ""
        if isinstance(brand_raw, list):
            brand = brand_raw[0] if brand_raw else extract_brand(name)
        elif isinstance(brand_raw, str):
            brand = brand_raw
        else:
            brand = extract_brand(name)

        variant = item.get("variant_name") or item.get("shade") or ""

        in_stock = item.get("inStock", True)
        if isinstance(in_stock, str):
            in_stock = in_stock.lower() not in ("0", "false", "no")

        return ProductResult(
            name=name,
            brand=brand,
            price=price,
            mrp=mrp if mrp > 0 else price,
            discount_percent=discount,
            image_url=image_url,
            product_url=product_url,
            platform=Platform.NYKAA,
            in_stock=bool(in_stock),
            rating=rating,
            rating_count=rating_count,
            variant=variant,
        )
