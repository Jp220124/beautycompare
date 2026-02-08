from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "BeautyCompare"
    debug: bool = True
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # Cache
    cache_ttl_seconds: int = 7200  # 2 hours
    cache_max_size: int = 500

    # Scraping
    request_timeout: int = 15  # seconds per adapter
    max_retries: int = 2
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    # Rate limiting
    rate_limit: str = "10/minute"

    # Database
    database_url: str = "sqlite+aiosqlite:///./beautycompare.db"

    # Amazon PA-API (optional)
    amazon_access_key: str = ""
    amazon_secret_key: str = ""
    amazon_partner_tag: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
