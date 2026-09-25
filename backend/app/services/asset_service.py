"""Servicio de gestión de activos."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.dto import AssetSnapshotDTO
from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.services.calculation_service import CalculationService


class AssetService:
    """Lógica de negocio para activos."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AssetRepository(db)
        self.calc_service = CalculationService(db)

    def create_asset(self, data: dict[str, Any]) -> Asset:
        """Crea un activo nuevo."""
        existing = self.repo.get_by_ticker(data["ticker"], data.get("asset_type"))
        if existing is not None:
            raise ValueError(f"Asset with ticker '{data['ticker']}' already exists")

        current_price = data.pop("current_price", None)
        asset = Asset(**data)
        if current_price is not None:
            asset.current_price = current_price
            from datetime import datetime

            asset.price_updated_at = datetime.utcnow()
            asset.manual_price = True
        return self.repo.create(asset)

    def update_asset(self, asset_id: int, data: dict[str, Any]) -> Asset | None:
        """Actualiza un activo existente."""
        return self.repo.update(asset_id, data)

    def deprecate_asset(self, asset_id: int) -> Asset | None:
        """Marca un activo como inactivo."""
        return self.repo.update(asset_id, {"is_active": False})

    def search_assets(self, query: str) -> list[Asset]:
        """Busca activos por ticker o nombre."""
        return self.repo.search(query)

    def get_asset_details(self, asset_id: int) -> dict[str, Any]:
        """Detalles de un activo: incluye precio, rentabilidad y cantidad."""
        asset = self.repo.get(asset_id)
        if asset is None:
            raise ValueError(f"Asset {asset_id} not found")

        holdings = self.calc_service.get_holdings(asset_id)
        returns = self.calc_service.calculate_total_return(asset_id)

        return {
            "asset": asset,
            "holdings": holdings,
            "returns": returns,
        }

    def get_all_assets_snapshot(self) -> list[AssetSnapshotDTO]:
        """Snapshot de todos los activos."""
        return self.calc_service.get_all_assets_snapshot()
