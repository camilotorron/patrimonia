"""Modelo: AccountBalance (histórico de saldos de una cuenta)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.account import Account


class AccountBalance(Base):
    """Registro de saldo de una cuenta en un momento dado."""

    __tablename__ = "account_balances"

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=18, scale=2), nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Relationships
    account: Mapped["Account"] = relationship()
