"""Repository para la entidad Operation."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import OperationType
from app.models.operation import Operation
from app.repositories.base import BaseRepository


class OperationRepository(BaseRepository[Operation]):
    """Acceso a datos para operaciones."""

    model = Operation

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_asset(self, asset_id: int) -> list[Operation]:
        stmt = (
            select(Operation)
            .where(Operation.asset_id == asset_id)
            .order_by(Operation.operation_date)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_account(self, account_id: int) -> list[Operation]:
        stmt = (
            select(Operation)
            .where(Operation.account_id == account_id)
            .order_by(Operation.operation_date)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_date_range(self, start: datetime, end: datetime) -> list[Operation]:
        stmt = (
            select(Operation)
            .where(
                Operation.operation_date >= start,
                Operation.operation_date <= end,
            )
            .order_by(Operation.operation_date)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_since(self, date: datetime) -> list[Operation]:
        stmt = (
            select(Operation)
            .where(Operation.operation_date >= date)
            .order_by(Operation.operation_date)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_type(self, operation_type: OperationType) -> list[Operation]:
        stmt = select(Operation).where(Operation.operation_type == operation_type)
        return list(self.db.execute(stmt).scalars().all())
