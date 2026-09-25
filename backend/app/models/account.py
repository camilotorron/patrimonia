"""Modelo: Account (cuentas corrientes / ahorro / inversión)."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.enums import AccountType

if TYPE_CHECKING:
    from app.models.operation import Operation


class Account(Base):
    """Cuenta financiera: corriente, ahorro o inversión."""

    __tablename__ = "accounts"

    name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    account_type: Mapped[AccountType] = mapped_column(nullable=False)
    bank: Mapped[str] = mapped_column(String(255), nullable=False)
    iban: Mapped[str | None] = mapped_column(String(64), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    current_balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False, default=Decimal("0")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    operations: Mapped[List["Operation"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
