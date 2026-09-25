"""Modelo: Asset (acciones, ETFs, fondos, criptos)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import AssetType

if TYPE_CHECKING:
    from app.models.operation import Operation
    from app.models.price import Price


class Asset(Base):
    """Activo financiero rastreable."""

    __tablename__ = "assets"

    ticker: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    asset_type: Mapped[AssetType] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    current_price: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=18, scale=6), nullable=True
    )
    price_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    manual_price: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    operations: Mapped[List["Operation"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )
    prices: Mapped[List["Price"]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )
