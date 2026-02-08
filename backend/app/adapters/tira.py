import logging
import base64
import re

from curl_cffi.requests import AsyncSession

from app.adapters.base import BaseAdapter
from app.models.schemas import ProductResult, Platform
from app.config import get_settings
from app.utils.text import clean_price, extract_brand, compute_discount

logger = logging.getLogger(__name__)
settings = get_settings()


class TiraAdapter(BaseAdapter):
    """Adapter for Tira Beauty using the Fynd Platform catalog API."""

    APP_ID = "62d53777f5ad942d3e505f77"
    APP_TOKEN = "ikdiQv6tj"
    API_URL = "https://api.tirabeauty.com/service/application/catalog/v1.0/products/"

    @property
    def platform(self) -> Platform:
        return Platform.TIRA

    @property
    def platform_name(self) -> str:
        return "Tira Beauty"

    @property
    def base_url(self) -> str:
        return "https://www.tirabeauty.com"

    def _auth_header(self) -> str:
        token = base64.b64encode(f"{self.APP_ID}:{self.APP_TOKEN}".encode()).decode()
        return f"Bearer {token}"

    async def search(self, query: str, limit: int = 10) -> list[ProductResult]:
        results: list[ProductResult] = []
        try:
            async with AsyncSession(impersonate="chrome131") as s:
                headers = {
                    "Accept": "application/json",
                    "Authorization": self._auth_header(),
                }
                resp = await s.get(
                    self.API_URL,
                    params={"q": query, "page_size": limit},
                    headers=headers,
                    timeout=settings.request_timeout,
                )
                if resp.status_code != 200:
                    logger.warning(f"Tira API returned {resp.status_code}")
                    return []

                data = resp.json()
                items = data.get("items", [])

                for item in items[:limit]:
                    try:
                        result = self._parse_product(item)
                        if result:
                            results.append(result)
                    except Exception as e:
                        logger.warning(f"Tira: failed to parse product: {e}")
                        continue

        except Exception as e:
            logger.error(f"Tira: unexpected error: {e}")

        return results

    def _parse_product(self, item: dict) -> ProductResult | None:
        name = item.get("name") or ""
        if not name:
            return None

        # Price structure: {marked: {min, max}, effective: {min, max}, selling: {min, max}}
        price_data = item.get("price", {})
        effective = price_data.get("effective", {})
        marked = price_data.get("marked", {})

        price = effective.get("min") or effective.get("max") or 0.0
        mrp = marked.get("min") or marked.get("max") or 0.0

        if price <= 0:
            return None

        discount = compute_discount(price, mrp)

        # Brand
        brand_data = item.get("brand", {})
        brand = brand_data.get("name", "") if isinstance(brand_data, dict) else str(brand_data)
        if not brand:
            brand = extract_brand(name)

        # Image from medias array
        image_url = ""
        medias = item.get("medias", [])
        if medias and isinstance(medias[0], dict):
            image_url = medias[0].get("url", "")

        # Product URL from slug
        slug = item.get("slug", "")
        product_url = f"https://www.tirabeauty.com/product/{slug}" if slug else ""

        # In stock
        in_stock = item.get("sellable", True)

        # Extract discount from string like "10% OFF"
        discount_str = item.get("discount", "")
        if discount_str and discount == 0:
            match = re.search(r"(\d+)%", discount_str)
            if match:
                discount = float(match.group(1))

        return ProductResult(
            name=name,
            brand=brand,
            price=price,
            mrp=mrp if mrp > 0 else price,
            discount_percent=discount,
            image_url=image_url,
            product_url=product_url,
            platform=Platform.TIRA,
            in_stock=bool(in_stock),
            rating=0,
        )
