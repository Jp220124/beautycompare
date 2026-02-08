from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship

from app.config import get_settings

settings = get_settings()

_engine_kwargs: dict = {"echo": settings.debug}

# PostgreSQL needs pool settings; SQLite doesn't support them
if settings.database_url.startswith("postgresql"):
    _engine_kwargs.update({"pool_size": 5, "max_overflow": 10, "pool_pre_ping": True})

engine = create_async_engine(settings.database_url, **_engine_kwargs)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    brand = Column(String(200), default="")
    normalized_name = Column(String(500), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    prices = relationship("PriceRecord", back_populates="product")


class PriceRecord(Base):
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    mrp = Column(Float, default=0)
    discount_percent = Column(Float, default=0)
    product_url = Column(Text, default="")
    in_stock = Column(Boolean, default=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="prices")


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(String(500), nullable=False, index=True)
    results_count = Column(Integer, default=0)
    response_time_ms = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
