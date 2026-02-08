import logging
from rapidfuzz import fuzz
from app.models.schemas import ProductResult, MatchedProduct
from app.utils.text import normalize_text, extract_brand, extract_size

logger = logging.getLogger(__name__)

MATCH_THRESHOLD = 60  # minimum similarity score to consider a match


def match_products(
    all_results: dict[str, list[ProductResult]],
) -> list[MatchedProduct]:
    """
    Group products across platforms that refer to the same item.

    Args:
        all_results: dict mapping platform name -> list of ProductResult

    Returns:
        List of MatchedProduct with prices from multiple platforms.
    """
    # Flatten all products with platform labels
    flat: list[ProductResult] = []
    for products in all_results.values():
        flat.extend(products)

    if not flat:
        return []

    # Build groups using greedy matching
    used: set[int] = set()
    groups: list[list[ProductResult]] = []

    for i, product_a in enumerate(flat):
        if i in used:
            continue

        group = [product_a]
        used.add(i)

        for j, product_b in enumerate(flat):
            if j in used:
                continue
            # Don't match products from the same platform
            if product_a.platform == product_b.platform:
                continue

            score = _similarity_score(product_a, product_b)
            if score >= MATCH_THRESHOLD:
                group.append(product_b)
                used.add(j)

        groups.append(group)

    # Also add unmatched products as single-platform entries
    for i, product in enumerate(flat):
        if i not in used:
            groups.append([product])
            used.add(i)

    # Convert groups to MatchedProduct objects
    matched: list[MatchedProduct] = []
    for group in groups:
        mp = _build_matched_product(group)
        matched.append(mp)

    # Sort by number of platforms (more = better match), then by best price
    matched.sort(key=lambda m: (-len(m.prices), m.best_price))

    return matched


def _similarity_score(a: ProductResult, b: ProductResult) -> float:
    """Compute a combined similarity score between two products (0-100)."""
    name_a = normalize_text(a.name)
    name_b = normalize_text(b.name)

    # Fuzzy name similarity (token_sort handles word reordering)
    name_score = fuzz.token_sort_ratio(name_a, name_b)

    # Brand match bonus
    brand_a = normalize_text(a.brand) if a.brand else extract_brand(a.name).lower()
    brand_b = normalize_text(b.brand) if b.brand else extract_brand(b.name).lower()
    brand_bonus = 15 if brand_a and brand_b and brand_a == brand_b else 0

    # Size match bonus / penalty
    size_a = extract_size(a.name)
    size_b = extract_size(b.name)
    size_mod = 0
    if size_a and size_b:
        size_mod = 10 if size_a == size_b else -20  # penalize size mismatch

    # Price proximity bonus (products at wildly different prices are likely different)
    price_mod = 0
    if a.price > 0 and b.price > 0:
        ratio = min(a.price, b.price) / max(a.price, b.price)
        if ratio > 0.7:
            price_mod = 5
        elif ratio < 0.3:
            price_mod = -15

    total = name_score + brand_bonus + size_mod + price_mod
    return min(max(total, 0), 100)


def _build_matched_product(group: list[ProductResult]) -> MatchedProduct:
    """Build a MatchedProduct from a group of matched ProductResults."""
    # Use the first product's name/brand as the canonical one
    primary = group[0]

    prices = sorted(group, key=lambda p: p.price)
    best = prices[0]
    worst = prices[-1]

    return MatchedProduct(
        product_name=primary.name,
        brand=primary.brand,
        variant=primary.variant,
        image_url=primary.image_url or next((p.image_url for p in group if p.image_url), ""),
        prices=group,
        best_price=best.price,
        best_platform=best.platform.value,
        savings=round(worst.price - best.price, 2) if len(group) > 1 else 0,
    )
