"""Modelo: Operation (compra/venta de activos)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import OperationType

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.asset import Asset


class Operation(Base):
    """Operación de compra o venta de un activo en una cuenta."""

    __tablename__ = "operations"
    __table_args__ = (
        UniqueConstraint(
            "asset_id", "account_id", "operation_date", name="uq_operation"
        ),
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    operation_type: Mapped[OperationType] = mapped_column(nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=8), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=6), nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2), nullable=False
    )
    commission: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=Decimal("0")
    )
    operation_date: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    notes: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Relationships
    asset: Mapped["Asset"] = relationship(back_populates="operations")
    account: Mapped["Account"] = relationship(back_populates="operations")
