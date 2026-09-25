"""Repository para la entidad Account."""

from __future__ import annotations

from decimal import Decimal
from typing import override

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.enums import AccountType
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Acceso a datos para cuentas."""

    model = Account

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    # ------------------------------------------------------------------ #
    # Queries específicas
    # ------------------------------------------------------------------ #
    def get_by_name(self, name: str) -> Account | None:
        stmt = select(Account).where(Account.name == name)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_active(self) -> list[Account]:
        stmt = select(Account).where(Account.is_active.is_(True))
        return list(self.db.execute(stmt).scalars().all())

    def get_by_type(self, account_type: AccountType) -> list[Account]:
        stmt = select(Account).where(Account.account_type == account_type)
        return list(self.db.execute(stmt).scalars().all())
