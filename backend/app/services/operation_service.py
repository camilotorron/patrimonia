"""Servicio de gestión de operaciones (compra/venta).

Contiene la lógica de negocio para crear, validar y revertir operaciones,
incluyendo la actualización de saldos de cuentas.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.dto import HoldingsDTO
from app.models.enums import OperationType
from app.models.operation import Operation
from app.repositories.account_repository import AccountRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.operation_repository import OperationRepository
from app.services.calculation_service import CalculationService
from app.utils.helpers import safe_divide


class OperationService:
    """Lógica de negocio para operaciones de compra/venta."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.operation_repo = OperationRepository(db)
        self.account_repo = AccountRepository(db)
        self.asset_repo = AssetRepository(db)
        self.calc_service = CalculationService(db)

    # ------------------------------------------------------------------ #
    # Validación
    # ------------------------------------------------------------------ #
    @staticmethod
    def validate_operation(
        asset_id: int,
        account_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        commission: Decimal,
        operation_date: datetime,
    ) -> tuple[bool, str]:
        """Valida los datos de una operación antes de crearla."""
        if quantity <= 0:
            return False, "Quantity must be positive"
        if unit_price <= 0:
            return False, "Unit price must be positive"
        if commission < 0:
            return False, "Commission cannot be negative"
        if operation_date > datetime.utcnow():
            return False, "Operation date cannot be in the future"
        if asset_id <= 0 or account_id <= 0:
            return False, "Invalid asset or account ID"
        return True, ""

    def _check_sell_quantity(self, asset_id: int, quantity: Decimal) -> bool:
        """Verifica que exista suficiente cantidad para vender."""
        qty, _ = self.calc_service._get_holdings(asset_id)  # noqa: SLF001
        return qty >= quantity

    # ------------------------------------------------------------------ #
    # Creación
    # ------------------------------------------------------------------ #
    def create_buy_operation(
        self,
        asset_id: int,
        account_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        commission: Decimal = Decimal("0"),
        operation_date: datetime | None = None,
        notes: str | None = None,
    ) -> Operation:
        """Crea una operación de compra y actualiza el saldo de la cuenta."""
        op_date = operation_date or datetime.utcnow()
        valid, msg = self.validate_operation(
            asset_id, account_id, quantity, unit_price, commission, op_date
        )
        if not valid:
            raise ValueError(msg)

        asset = self.asset_repo.get(asset_id)
        if asset is None:
            raise ValueError(f"Asset {asset_id} not found")

        account = self.account_repo.get(account_id)
        if account is None:
            raise ValueError(f"Account {account_id} not found")

        total_amount = quantity * unit_price + commission

        op = Operation(
            asset_id=asset_id,
            account_id=account_id,
            operation_type=OperationType.BUY,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            commission=commission,
            operation_date=op_date,
            notes=notes,
        )
        self.operation_repo.create(op)

        # Actualizar saldo de la cuenta (restar la compra)
        account.current_balance -= total_amount
        self.db.flush()

        return op

    def create_sell_operation(
        self,
        asset_id: int,
        account_id: int,
        quantity: Decimal,
        unit_price: Decimal,
        commission: Decimal = Decimal("0"),
        operation_date: datetime | None = None,
        notes: str | None = None,
    ) -> Operation:
        """Crea una operación de venta y actualiza el saldo de la cuenta."""
        op_date = operation_date or datetime.utcnow()
        valid, msg = self.validate_operation(
            asset_id, account_id, quantity, unit_price, commission, op_date
        )
        if not valid:
            raise ValueError(msg)

        if not self._check_sell_quantity(asset_id, quantity):
            raise ValueError("Insufficient quantity to sell")

        asset = self.asset_repo.get(asset_id)
        if asset is None:
            raise ValueError(f"Asset {asset_id} not found")

        account = self.account_repo.get(account_id)
        if account is None:
            raise ValueError(f"Account {account_id} not found")

        total_amount = quantity * unit_price - commission

        op = Operation(
            asset_id=asset_id,
            account_id=account_id,
            operation_type=OperationType.SELL,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            commission=commission,
            operation_date=op_date,
            notes=notes,
        )
        self.operation_repo.create(op)

        # Actualizar saldo de la cuenta (sumar la venta)
        account.current_balance += total_amount
        self.db.flush()

        return op

    # ------------------------------------------------------------------ #
    # Gestión
    # ------------------------------------------------------------------ #
    def update_operation(self, op_id: int, data: dict[str, Any]) -> Operation | None:
        """Actualiza una operación (solo si es reciente: < 7 días)."""
        op = self.operation_repo.get(op_id)
        if op is None:
            return None
        days_since = (datetime.utcnow() - op.operation_date).days
        if days_since > 7:
            raise ValueError("Cannot edit operations older than 7 days")
        return self.operation_repo.update(op_id, data)

    def cancel_operation(self, op_id: int) -> bool:
        """Revierte una operación: ajusta el saldo y elimina la operación."""
        op = self.operation_repo.get(op_id)
        if op is None:
            return False

        account = self.account_repo.get(op.account_id)
        if account is None:
            return False

        if op.operation_type == OperationType.BUY:
            # Revertir compra: sumar de vuelta el dinero
            account.current_balance += op.total_amount
        else:
            # Revertir venta: restar el dinero
            account.current_balance -= op.total_amount

        self.db.flush()
        return self.operation_repo.delete(op_id)

    def get_holdings(self, asset_id: int) -> HoldingsDTO:
        """Delega al servicio de cálculo."""
        return self.calc_service.get_holdings(asset_id)
