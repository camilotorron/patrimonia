"""Scheduler de tareas en background con APScheduler."""

from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _update_all_prices_job() -> None:
    """Job: actualiza todos los precios activos."""
    from app.database import get_db_context
    from app.services.price_service import PriceService

    logger.info("Starting scheduled price update")
    try:
        with get_db_context() as db:
            service = PriceService(db)
            result = service.refresh_all_prices()
            logger.info(
                "Scheduled price update done: %d updated, %d failed",
                result.updated_count,
                result.failed_count,
            )
    except Exception:
        logger.exception("Scheduled price update failed")


def _cleanup_cache_job() -> None:
    """Job: limpia entradas de caché expiradas."""
    from app.services.cache_service import price_cache_service

    removed = price_cache_service.cleanup_expired()
    logger.info("Cache cleanup: removed %d entries", removed)


def start_scheduler() -> None:
    """Inicia el scheduler de background."""
    global _scheduler  # noqa: PLW0603
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler()

    # Actualizar precios diariamente a las 18:00
    _scheduler.add_job(
        _update_all_prices_job,
        CronTrigger(hour=18, minute=0),
        id="update_prices",
        replace_existing=True,
    )

    # Limpiar caché cada hora
    _scheduler.add_job(
        _cleanup_cache_job,
        IntervalTrigger(hours=1),
        id="cleanup_cache",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("Scheduler started with jobs: update_prices, cleanup_cache")


def shutdown_scheduler() -> None:
    """Detiene el scheduler."""
    global _scheduler  # noqa: PLW0603
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("Scheduler shut down")
