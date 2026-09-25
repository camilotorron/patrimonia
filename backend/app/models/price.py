"""Modelo: Price (histórico de precios de un activo)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import PriceSource

if TYPE_CHECKING:
    from app.models.asset import Asset


class Price(Base):
    """Registro de precio histórico de un activo."""

    __tablename__ = "prices"
    __table_args__ = (
        UniqueConstraint("asset_id", "price_date", name="uq_price_asset_date"),
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=6), nullable=False
    )
    price_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    source: Mapped[PriceSource] = mapped_column(
        nullable=False, default=PriceSource.YFINANCE
    )

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="prices")
