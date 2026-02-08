import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_settings
from app.routers import search
from app.models.database import init_db

logging.basicConfig(level=logging.INFO)
settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    description="Compare beauty product prices across Nykaa, Tira & Amazon India",
    version="0.1.0",
)

app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Rate limiting error handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Routers
app.include_router(search.router, prefix="/api")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "app": settings.app_name}
