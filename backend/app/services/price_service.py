"""Servicio orquestador de precios.

Combina caché → proveedor externo (yfinance) → última conocida en BD.
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import settings
from app.dto import BulkRefreshResultDTO, PriceRefreshResultDTO
from app.models.enums import PriceSource
from app.models.price import Price
from app.repositories.asset_repository import AssetRepository
from app.repositories.price_repository import PriceRepository
from app.services.cache_service import price_cache_service
from app.services.price_provider import YFinancePriceProvider

logger = logging.getLogger(__name__)


class PriceService:
    """Orquesta la obtención y almacenamiento de precios."""

    def __init__(
        self,
        db: Session,
        provider: YFinancePriceProvider | None = None,
    ) -> None:
        self.db = db
        self.asset_repo = AssetRepository(db)
        self.price_repo = PriceRepository(db)
        self.provider = provider or YFinancePriceProvider()

    # ------------------------------------------------------------------ #
    # Lectura de precios
    # ------------------------------------------------------------------ #
    def get_current_price(self, asset_id: int) -> Decimal | None:
        """Obtiene el precio actual: caché → BD (último) → None."""
        # 1. Caché
        cached = price_cache_service.get_cached_price(asset_id)
        if cached is not None:
            return cached[0]

        # 2. Último precio en BD
        latest = self.price_repo.get_latest(asset_id)
        if latest is not None:
            return latest.price

        # 3. Precio guardado en el asset
        asset = self.asset_repo.get(asset_id)
        if asset is not None:
            return asset.current_price

        return None

    # ------------------------------------------------------------------ #
    # Actualización de precios
    # ------------------------------------------------------------------ #
    def refresh_asset_price(self, asset_id: int) -> PriceRefreshResultDTO:
        """Fuerza la actualización de un precio desde yfinance."""
        asset = self.asset_repo.get(asset_id)
        if asset is None:
            return PriceRefreshResultDTO(
                asset_id=asset_id,
                ticker="UNKNOWN",
                old_price=None,
                new_price=Decimal("0"),
                timestamp=datetime.utcnow(),
                success=False,
                error="Asset not found",
            )

        if asset.manual_price:
            return PriceRefreshResultDTO(
                asset_id=asset_id,
                ticker=asset.ticker,
                old_price=asset.current_price,
                new_price=asset.current_price or Decimal("0"),
                timestamp=datetime.utcnow(),
                success=True,
            )

        old_price = asset.current_price

        try:
            new_price = self.provider.get_price(asset.ticker)
        except Exception as exc:
            logger.error("Failed to fetch price for %s: %s", asset.ticker, exc)
            return PriceRefreshResultDTO(
                asset_id=asset_id,
                ticker=asset.ticker,
                old_price=old_price,
                new_price=old_price or Decimal("0"),
                timestamp=datetime.utcnow(),
                success=False,
                error=str(exc),
            )

        if new_price is None:
            return PriceRefreshResultDTO(
                asset_id=asset_id,
                ticker=asset.ticker,
                old_price=old_price,
                new_price=old_price or Decimal("0"),
                timestamp=datetime.utcnow(),
                success=False,
                error="Price not found",
            )

        now = datetime.utcnow()

        # Guardar en caché
        price_cache_service.set_cached_price(
            asset_id, new_price, ttl=settings.PRICE_CACHE_TTL
        )

        # Guardar en BD
        price = Price(
            asset_id=asset_id,
            price=new_price,
            price_date=now,
            source=PriceSource.YFINANCE,
        )
        self.price_repo.create(price)

        # Actualizar el asset
        self.asset_repo.update_current_price(asset_id, new_price, now)

        self.db.commit()

        return PriceRefreshResultDTO(
            asset_id=asset_id,
            ticker=asset.ticker,
            old_price=old_price,
            new_price=new_price,
            timestamp=now,
            success=True,
        )

    def refresh_all_prices(self) -> BulkRefreshResultDTO:
        """Actualiza los precios de todos los activos activos."""
        assets = self.asset_repo.get_active()
        updated: list[PriceRefreshResultDTO] = []
        failed: list[PriceRefreshResultDTO] = []

        for asset in assets:
            result = self.refresh_asset_price(asset.id)
            if result.success:
                updated.append(result)
            else:
                failed.append(result)

        logger.info(
            "Price refresh complete: %d updated, %d failed",
            len(updated),
            len(failed),
        )
        return BulkRefreshResultDTO(updated=updated, failed=failed)

    # ------------------------------------------------------------------ #
    # Histórico
    # ------------------------------------------------------------------ #
    def get_price_history(
        self, asset_id: int, start: datetime | None = None, end: datetime | None = None
    ) -> list[Price]:
        """Historial de precios de un activo."""
        return self.price_repo.get_history(asset_id, start, end)
