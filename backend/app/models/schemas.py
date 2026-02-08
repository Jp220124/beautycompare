from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Platform(str, Enum):
    NYKAA = "nykaa"
    AMAZON = "amazon"
    TIRA = "tira"


class ProductResult(BaseModel):
    """A single product result from one platform."""

    name: str
    brand: str = ""
    price: float = Field(description="Current selling price in INR")
    mrp: float = Field(0, description="Maximum retail price in INR")
    discount_percent: float = 0
    image_url: str = ""
    product_url: str = ""
    platform: Platform
    in_stock: bool = True
    rating: float = 0
    rating_count: int = 0
    variant: str = ""  # shade, size, etc.


class MatchedProduct(BaseModel):
    """A product matched across multiple platforms."""

    product_name: str
    brand: str = ""
    variant: str = ""
    image_url: str = ""
    prices: list[ProductResult] = []
    best_price: float = 0
    best_platform: str = ""
    savings: float = Field(0, description="Max price - Min price across platforms")


class SearchResponse(BaseModel):
    """API response for a search query."""

    query: str
    results: list[MatchedProduct] = []
    total_results: int = 0
    platforms_searched: list[str] = []
    platforms_failed: list[str] = []
    cached: bool = False
    search_time_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
