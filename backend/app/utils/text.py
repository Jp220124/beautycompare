import re
import unicodedata


def normalize_text(text: str) -> str:
    """Lowercase, strip, collapse whitespace, remove special chars."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"[^\w\s\-.]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def clean_price(text: str) -> float:
    """Extract numeric price from strings like 'Rs. 1,299', '₹1299', 'MRP: 599.00'."""
    if not text:
        return 0.0
    cleaned = re.sub(r"[^\d.]", "", str(text))
    if not cleaned:
        return 0.0
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_brand(text: str) -> str:
    """Extract brand name (first word group before product line)."""
    known_brands = [
        "maybelline", "lakme", "mac", "nykaa", "sugar", "colorbar",
        "neutrogena", "loreal", "garnier", "biotique", "mamaearth",
        "plum", "minimalist", "cetaphil", "cerave", "the ordinary",
        "innisfree", "forest essentials", "kama ayurveda", "dot & key",
        "mars", "faces canada", "revlon", "elle 18", "blue heaven",
        "himalaya", "nivea", "dove", "ponds", "olay", "simple",
        "st. botanica", "wow", "mcaffeine", "re'equil", "derma co",
    ]
    text_lower = text.lower()
    for brand in sorted(known_brands, key=len, reverse=True):
        if brand in text_lower:
            return brand.title()
    # Fallback: first word
    parts = text.strip().split()
    return parts[0] if parts else ""


_SIZE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(ml|g|gm|kg|l|ltr|oz|fl\.?\s*oz)\b",
    re.IGNORECASE,
)


def extract_size(text: str) -> str:
    """Extract size like '30ml', '50g' from product name."""
    match = _SIZE_PATTERN.search(text)
    if match:
        value = match.group(1)
        unit = match.group(2).lower().replace(" ", "")
        if unit == "gm":
            unit = "g"
        if unit in ("ltr",):
            unit = "l"
        return f"{value}{unit}"
    return ""


_SHADE_PATTERN = re.compile(
    r"(?:#?\s*(\d{2,4}))\s*[-–]?\s*([a-zA-Z\s]+)?|shade\s*[:.]?\s*(\w+)",
    re.IGNORECASE,
)


def extract_shade(text: str) -> str:
    """Extract shade number/name like '128 Warm Nude'."""
    match = _SHADE_PATTERN.search(text)
    if match:
        return match.group(0).strip()
    return ""


def compute_discount(price: float, mrp: float) -> float:
    """Calculate discount percentage."""
    if mrp <= 0 or price <= 0 or price >= mrp:
        return 0.0
    return round(((mrp - price) / mrp) * 100, 1)
