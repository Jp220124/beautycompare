from abc import ABC, abstractmethod

from app.models.schemas import ProductResult, Platform


class BaseAdapter(ABC):
    """Abstract base class for all platform adapters."""

    @property
    @abstractmethod
    def platform(self) -> Platform:
        """Return the platform identifier."""
        ...

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the human-readable platform name."""
        ...

    @property
    def base_url(self) -> str:
        return ""

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[ProductResult]:
        """
        Search for products matching the query.
        Returns a list of ProductResult from this platform.
        """
        ...

    async def close(self) -> None:
        """Cleanup resources. Override if adapter holds connections."""
        pass
