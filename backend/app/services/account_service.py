"""Servicio de gestión de cuentas."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.dto import AccountSummaryDTO
from app.models.account import Account
from app.repositories.account_repository import AccountRepository
from app.repositories.operation_repository import OperationRepository
from app.services.calculation_service import CalculationService


class AccountService:
    """Lógica de negocio para cuentas."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AccountRepository(db)
        self.operation_repo = OperationRepository(db)
        self.calc_service = CalculationService(db)

    def create_account(self, data: dict[str, Any]) -> Account:
        """Crea una cuenta nueva."""
        if self.repo.get_by_name(data["name"]) is not None:
            raise ValueError(f"Account with name '{data['name']}' already exists")
        account = Account(**data)
        return self.repo.create(account)

    def update_account(self, account_id: int, data: dict[str, Any]) -> Account | None:
        """Actualiza una cuenta existente."""
        return self.repo.update(account_id, data)

    def delete_account(self, account_id: int) -> bool:
        """Elimina una cuenta (soft delete si tiene operaciones)."""
        account = self.repo.get(account_id)
        if account is None:
            return False

        ops = self.operation_repo.get_by_account(account_id)
        if ops:
            # Soft delete: marcar como inactiva
            account.is_active = False
            self.db.flush()
            return True

        return self.repo.delete(account_id)

    def close_account(self, account_id: int) -> bool:
        """Cierra una cuenta (soft delete)."""
        account = self.repo.get(account_id)
        if account is None:
            return False
        account.is_active = False
        self.db.flush()
        return True

    def transfer_funds(self, from_id: int, to_id: int, amount: Decimal) -> bool:
        """Transfiere fondos entre dos cuentas."""
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")

        from_account = self.repo.get(from_id)
        to_account = self.repo.get(to_id)

        if from_account is None or to_account is None:
            raise ValueError("Account not found")
        if from_account.current_balance < amount:
            raise ValueError("Insufficient balance for transfer")

        from_account.current_balance -= amount
        to_account.current_balance += amount
        self.db.flush()
        return True

    def get_account_summary(self, account_id: int) -> AccountSummaryDTO:
        """Resumen de una cuenta."""
        return self.calc_service.get_account_summary(account_id)
