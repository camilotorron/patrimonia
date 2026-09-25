"""Repository para la entidad Asset."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.enums import AssetType
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """Acceso a datos para activos."""

    model = Asset

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_ticker(
        self, ticker: str, asset_type: AssetType | None = None
    ) -> Asset | None:
        stmt = select(Asset).where(Asset.ticker == ticker.upper())
        if asset_type is not None:
            stmt = stmt.where(Asset.asset_type == asset_type)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_type(self, asset_type: AssetType) -> list[Asset]:
        stmt = select(Asset).where(Asset.asset_type == asset_type)
        return list(self.db.execute(stmt).scalars().all())

    def get_active(self) -> list[Asset]:
        stmt = select(Asset).where(Asset.is_active.is_(True))
        return list(self.db.execute(stmt).scalars().all())

    def search(self, query: str) -> list[Asset]:
        pattern = f"%{query}%"
        stmt = select(Asset).where(
            (Asset.ticker.ilike(pattern)) | (Asset.name.ilike(pattern))
        )
        return list(self.db.execute(stmt).scalars().all())

    def update_current_price(
        self, asset_id: int, price: Decimal, timestamp: datetime | None = None
    ) -> Asset | None:
        asset = self.get(asset_id)
        if asset is None:
            return None
        asset.current_price = price
        asset.price_updated_at = timestamp or datetime.utcnow()
        self.db.flush()
        self.db.refresh(asset)
        return asset
