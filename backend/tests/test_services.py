"""Tests para los servicios de negocio."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.models.enums import OperationType
from app.services.account_service import AccountService
from app.services.asset_service import AssetService
from app.services.calculation_service import CalculationService
from app.services.operation_service import OperationService


class TestAccountService:
    def test_create_account(self, db_session):
        service = AccountService(db_session)
        account = service.create_account(
            {
                "name": "Nueva Cuenta",
                "account_type": "Corriente",
                "bank": "BBVA",
                "currency": "EUR",
                "current_balance": Decimal("5000"),
            }
        )
        assert account.id is not None
        assert account.name == "Nueva Cuenta"

    def test_create_duplicate_account_fails(self, db_session):
        service = AccountService(db_session)
        service.create_account(
            {
                "name": "Dup",
                "account_type": "Corriente",
                "bank": "Bank",
                "currency": "EUR",
            }
        )
        with pytest.raises(ValueError, match="already exists"):
            service.create_account(
                {
                    "name": "Dup",
                    "account_type": "Corriente",
                    "bank": "Bank",
                    "currency": "EUR",
                }
            )

    def test_transfer_funds(self, db_session):
        service = AccountService(db_session)
        from app.models.account import Account
        from app.models.enums import AccountType

        a1 = Account(
            name="A",
            account_type=AccountType.CORRIENTE,
            bank="B",
            current_balance=Decimal("1000"),
        )
        a2 = Account(
            name="C",
            account_type=AccountType.CORRIENTE,
            bank="B",
            current_balance=Decimal("500"),
        )
        db_session.add_all([a1, a2])
        db_session.commit()

        service.transfer_funds(a1.id, a2.id, Decimal("300"))
        db_session.refresh(a1)
        db_session.refresh(a2)
        assert a1.current_balance == Decimal("700")
        assert a2.current_balance == Decimal("800")

    def test_transfer_insufficient_balance(self, db_session):
        service = AccountService(db_session)
        from app.models.account import Account
        from app.models.enums import AccountType

        a1 = Account(
            name="A",
            account_type=AccountType.CORRIENTE,
            bank="B",
            current_balance=Decimal("100"),
        )
        a2 = Account(
            name="C",
            account_type=AccountType.CORRIENTE,
            bank="B",
            current_balance=Decimal("0"),
        )
        db_session.add_all([a1, a2])
        db_session.commit()

        with pytest.raises(ValueError, match="Insufficient"):
            service.transfer_funds(a1.id, a2.id, Decimal("500"))

    def test_delete_account_with_operations_soft_delete(
        self, db_session, sample_account, sample_operation
    ):
        service = AccountService(db_session)
        service.delete_account(sample_account.id)
        db_session.refresh(sample_account)
        assert sample_account.is_active is False


class TestAssetService:
    def test_create_asset(self, db_session):
        service = AssetService(db_session)
        asset = service.create_asset(
            {
                "ticker": "MSFT",
                "asset_type": "Stock",
                "name": "Microsoft",
                "currency": "USD",
            }
        )
        assert asset.id is not None
        assert asset.ticker == "MSFT"

    def test_create_duplicate_asset_fails(self, db_session):
        service = AssetService(db_session)
        service.create_asset(
            {
                "ticker": "GOOG",
                "asset_type": "Stock",
                "name": "Google",
                "currency": "USD",
            }
        )
        with pytest.raises(ValueError, match="already exists"):
            service.create_asset(
                {
                    "ticker": "GOOG",
                    "asset_type": "Stock",
                    "name": "Google",
                    "currency": "USD",
                }
            )

    def test_search_assets(self, db_session, sample_asset):
        service = AssetService(db_session)
        results = service.search_assets("AAPL")
        assert len(results) >= 1
        assert results[0].ticker == "AAPL"


class TestOperationService:
    def test_create_buy_operation(self, db_session, sample_account, sample_asset):
        service = OperationService(db_session)
        op = service.create_buy_operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            quantity=Decimal("10"),
            unit_price=Decimal("150"),
            commission=Decimal("5"),
        )
        db_session.refresh(sample_account)
        assert op.operation_type == OperationType.BUY
        assert sample_account.current_balance == Decimal("10000") - Decimal("1505")

    def test_create_sell_operation(self, db_session, sample_account, sample_asset):
        service = OperationService(db_session)
        # Comprar primero
        service.create_buy_operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            quantity=Decimal("20"),
            unit_price=Decimal("150"),
        )
        db_session.refresh(sample_account)
        balance_after_buy = sample_account.current_balance

        # Vender
        op = service.create_sell_operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            quantity=Decimal("10"),
            unit_price=Decimal("160"),
        )
        db_session.refresh(sample_account)
        assert op.operation_type == OperationType.SELL

    def test_sell_insufficient_quantity(self, db_session, sample_account, sample_asset):
        service = OperationService(db_session)
        with pytest.raises(ValueError, match="Insufficient"):
            service.create_sell_operation(
                asset_id=sample_asset.id,
                account_id=sample_account.id,
                quantity=Decimal("100"),
                unit_price=Decimal("150"),
            )

    def test_cancel_operation(self, db_session, sample_account, sample_operation):
        service = OperationService(db_session)
        original_balance = sample_account.current_balance
        # sample_operation es una compra de 1500 + 5 = 1505
        # Al crearla manualmente en fixtures no se restó del balance
        # así que primero ajustamos: simulamos que el balance ya fue restado
        result = service.cancel_operation(sample_operation.id)
        assert result is True

    def test_validate_operation(self):
        valid, msg = OperationService.validate_operation(
            1, 1, Decimal("10"), Decimal("100"), Decimal("5"), datetime.utcnow()
        )
        assert valid is True

        invalid, msg = OperationService.validate_operation(
            1, 1, Decimal("-1"), Decimal("100"), Decimal("0"), datetime.utcnow()
        )
        assert invalid is False
        assert "positive" in msg.lower()


class TestCalculationService:
    def test_calculate_asset_value(self, db_session):
        service = CalculationService(db_session)
        value = service.calculate_asset_value(Decimal("10"), Decimal("150"))
        assert value == Decimal("1500")

    def test_calculate_asset_value_no_price(self, db_session):
        service = CalculationService(db_session)
        value = service.calculate_asset_value(Decimal("10"), None)
        assert value == Decimal("0")

    def test_get_holdings(self, db_session, sample_account, sample_asset):
        op_service = OperationService(db_session)
        op_service.create_buy_operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            quantity=Decimal("10"),
            unit_price=Decimal("150"),
        )

        calc = CalculationService(db_session)
        holdings = calc.get_holdings(sample_asset.id)
        assert holdings.quantity == Decimal("10")
        assert holdings.total_invested == Decimal("1500") + Decimal("5")  # con comisión

    def test_calculate_total_wealth(self, db_session, sample_account, sample_asset):
        op_service = OperationService(db_session)
        op_service.create_buy_operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            quantity=Decimal("10"),
            unit_price=Decimal("150"),
        )

        calc = CalculationService(db_session)
        wealth = calc.calculate_total_wealth()
        # Saldo cuenta después de compra = 10000 - 1505 = 8495
        # Valor de activos = 10 * 150 = 1500
        # Total = 8495 + 1500 = 9995
        assert wealth == Decimal("9995")

    def test_calculate_portfolio_composition(
        self, db_session, sample_account, sample_asset
    ):
        op_service = OperationService(db_session)
        op_service.create_buy_operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            quantity=Decimal("10"),
            unit_price=Decimal("150"),
        )

        calc = CalculationService(db_session)
        composition = calc.calculate_portfolio_composition()
        assert len(composition) >= 1
        assert composition[0]["type"] == "Stock"
