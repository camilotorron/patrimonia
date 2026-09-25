"""Aplicación FastAPI principal."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import health_check, init_db

# ------------------------------------------------------------------ #
# Logging
# ------------------------------------------------------------------ #
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Lifespan
# ------------------------------------------------------------------ #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida de la aplicación."""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    init_db()

    # Intentar iniciar el scheduler de actualización de precios
    try:
        from app.services.scheduler import shutdown_scheduler, start_scheduler

        start_scheduler()
        logger.info("Price scheduler started")
        yield
        shutdown_scheduler()
    except Exception as exc:
        logger.warning("Scheduler not available: %s", exc)
        yield

    logger.info("Shutting down %s", settings.APP_NAME)


# ------------------------------------------------------------------ #
# App
# ------------------------------------------------------------------ #
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Aplicación web para trackear y monitorizar el patrimonio personal.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------ #
# Routers
# ------------------------------------------------------------------ #
from app.routes.accounts import router as accounts_router
from app.routes.assets import router as assets_router
from app.routes.operations import router as operations_router
from app.routes.pages import router as pages_router
from app.routes.prices import router as prices_router
from app.routes.reports import router as reports_router

API_V1 = "/api/v1"

app.include_router(accounts_router, prefix=f"{API_V1}/accounts", tags=["accounts"])
app.include_router(assets_router, prefix=f"{API_V1}/assets", tags=["assets"])
app.include_router(
    operations_router, prefix=f"{API_V1}/operations", tags=["operations"]
)
app.include_router(prices_router, prefix=f"{API_V1}/prices", tags=["prices"])
app.include_router(reports_router, prefix=f"{API_V1}/reports", tags=["reports"])
app.include_router(pages_router, tags=["pages"])

# ------------------------------------------------------------------ #
# Static files
# ------------------------------------------------------------------ #
_frontend_dir = settings.base_dir.parent / "frontend"
if _frontend_dir.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(_frontend_dir), html=True),
        name="frontend",
    )


# ------------------------------------------------------------------ #
# Health & version
# ------------------------------------------------------------------ #
@app.get("/health", tags=["health"])
async def health() -> dict:
    """Health check básico."""
    return {"status": "ok"}


@app.get("/health/detailed", tags=["health"])
async def health_detailed() -> dict:
    """Health check detallado con verificación de servicios."""
    db_ok = health_check()
    return {
        "status": "healthy" if db_ok else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "api": "ok",
            "db": "ok" if db_ok else "error",
        },
    }


@app.get("/version", tags=["health"])
async def version() -> dict:
    """Retorna nombre y versión de la aplicación."""
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION}
