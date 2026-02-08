import httpx
import logging
import re

from bs4 import BeautifulSoup

from app.adapters.base import BaseAdapter
from app.models.schemas import ProductResult, Platform
from app.config import get_settings
from app.utils.text import clean_price, extract_brand, compute_discount

logger = logging.getLogger(__name__)
settings = get_settings()


class AmazonAdapter(BaseAdapter):
    """Adapter for Amazon India using HTTP + BeautifulSoup scraping."""

    SEARCH_URL = "https://www.amazon.in/s"

    @property
    def platform(self) -> Platform:
        return Platform.AMAZON

    @property
    def platform_name(self) -> str:
        return "Amazon India"

    @property
    def base_url(self) -> str:
        return "https://www.amazon.in"

    def _headers(self) -> dict:
        return {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.amazon.in/",
            "DNT": "1",
        }

    async def search(self, query: str, limit: int = 10) -> list[ProductResult]:
        results: list[ProductResult] = []
        try:
            async with httpx.AsyncClient(
                timeout=settings.request_timeout, follow_redirects=True
            ) as client:
                params = {
                    "k": query,
                    "i": "beauty",  # search within beauty category
                    "ref": "nb_sb_noss",
                }
                resp = await client.get(
                    self.SEARCH_URL,
                    params=params,
                    headers=self._headers(),
                )
                resp.raise_for_status()
                results = self._parse_search_page(resp.text, limit)

        except httpx.TimeoutException:
            logger.error("Amazon: request timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"Amazon: HTTP {e.response.status_code}")
        except Exception as e:
            logger.error(f"Amazon: unexpected error: {e}")

        return results

    def _parse_search_page(self, html: str, limit: int) -> list[ProductResult]:
        soup = BeautifulSoup(html, "lxml")
        results: list[ProductResult] = []

        # Amazon search result cards
        cards = soup.select('[data-component-type="s-search-result"]')

        for card in cards[:limit * 2]:  # parse extra, filter later
            try:
                result = self._parse_card(card)
                if result:
                    results.append(result)
                    if len(results) >= limit:
                        break
            except Exception as e:
                logger.warning(f"Amazon: failed to parse card: {e}")
                continue

        return results

    def _parse_card(self, card) -> ProductResult | None:
        # Skip sponsored/ad results
        if card.select_one('[data-component-type="sp-sponsored-result"]'):
            return None
        # Also check for "Sponsored" label text
        sponsored_el = card.select_one('[class*="sponsored"], .puis-label-popover-default')
        if sponsored_el and "ponsored" in (sponsored_el.get_text() or ""):
            return None

        # Product name - try multiple strategies to get full title
        name = ""
        # Strategy 1: image alt text (most reliable - Amazon always puts full title here)
        img_el = card.select_one("img.s-image")
        if img_el:
            name = img_el.get("alt", "").strip()
        # Strategy 2: h2 full text with all spans
        if not name or len(name) < 10:
            h2_el = card.select_one("h2")
            if h2_el:
                name = h2_el.get_text(" ", strip=True)
        # Strategy 3: aria-label on card link
        if not name or len(name) < 10:
            h2_link = card.select_one("h2 a")
            if h2_link and h2_link.get("aria-label"):
                name = h2_link.get("aria-label", "")

        if not name or len(name) < 5:
            return None

        # Product URL
        link_el = card.select_one("h2 a")
        href = link_el.get("href", "") if link_el else ""
        product_url = f"https://www.amazon.in{href}" if href and not href.startswith("http") else href

        # Price - current selling price
        price = 0.0
        price_el = card.select_one("span.a-price span.a-offscreen")
        if price_el:
            price = clean_price(price_el.get_text())

        if price <= 0:
            # Try alternative price selector
            price_el = card.select_one(".a-price .a-price-whole")
            if price_el:
                price = clean_price(price_el.get_text())

        if price <= 0:
            return None

        # MRP (original price)
        mrp = 0.0
        mrp_el = card.select_one("span.a-price.a-text-price span.a-offscreen")
        if mrp_el:
            mrp = clean_price(mrp_el.get_text())

        discount = compute_discount(price, mrp) if mrp > 0 else 0.0

        # Image
        img_el = card.select_one("img.s-image")
        image_url = img_el.get("src", "") if img_el else ""

        # Rating
        rating = 0.0
        rating_el = card.select_one("span.a-icon-alt")
        if rating_el:
            rating_text = rating_el.get_text()
            match = re.search(r"([\d.]+)", rating_text)
            if match:
                rating = float(match.group(1))

        # Rating count
        rating_count = 0
        count_el = card.select_one('span[aria-label*="ratings"]') or card.select_one(
            ".a-size-base.s-underline-text"
        )
        if count_el:
            count_text = count_el.get_text().replace(",", "")
            match = re.search(r"([\d]+)", count_text)
            if match:
                rating_count = int(match.group(1))

        brand = extract_brand(name)

        return ProductResult(
            name=name,
            brand=brand,
            price=price,
            mrp=mrp if mrp > 0 else price,
            discount_percent=discount,
            image_url=image_url,
            product_url=product_url,
            platform=Platform.AMAZON,
            in_stock=True,
            rating=rating,
            rating_count=rating_count,
        )
