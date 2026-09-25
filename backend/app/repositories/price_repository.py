"""Repository para la entidad Price."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.price import Price
from app.repositories.base import BaseRepository


class PriceRepository(BaseRepository[Price]):
    """Acceso a datos para precios."""

    model = Price

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_latest(self, asset_id: int) -> Price | None:
        stmt = (
            select(Price)
            .where(Price.asset_id == asset_id)
            .order_by(Price.price_date.desc())
            .limit(1)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_date(self, asset_id: int, date: datetime) -> Price | None:
        stmt = select(Price).where(
            Price.asset_id == asset_id,
            Price.price_date == date,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_history(
        self, asset_id: int, start: datetime | None = None, end: datetime | None = None
    ) -> list[Price]:
        stmt = select(Price).where(Price.asset_id == asset_id)
        if start is not None:
            stmt = stmt.where(Price.price_date >= start)
        if end is not None:
            stmt = stmt.where(Price.price_date <= end)
        stmt = stmt.order_by(Price.price_date)
        return list(self.db.execute(stmt).scalars().all())
