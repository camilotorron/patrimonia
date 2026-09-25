"""Tests para los schemas de Pydantic."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.enums import AccountType, AssetType, OperationType
from app.schemas.account import AccountCreate
from app.schemas.asset import AssetCreate
from app.schemas.operation import OperationCreate
from app.schemas.price import PriceCreate


class TestAccountSchemas:
    def test_valid_account_create(self):
        account = AccountCreate(
            name="Mi Cuenta",
            account_type=AccountType.CORRIENTE,
            bank="Santander",
            currency="EUR",
            current_balance=Decimal("1000"),
        )
        assert account.name == "Mi Cuenta"
        assert account.currency == "EUR"

    def test_empty_name_fails(self):
        with pytest.raises(ValidationError):
            AccountCreate(name="", account_type=AccountType.CORRIENTE, bank="Bank")

    def test_negative_balance_fails(self):
        with pytest.raises(ValidationError):
            AccountCreate(
                name="Test",
                account_type=AccountType.CORRIENTE,
                bank="Bank",
                current_balance=Decimal("-100"),
            )

    def test_invalid_currency_fails(self):
        with pytest.raises(ValidationError):
            AccountCreate(
                name="Test",
                account_type=AccountType.CORRIENTE,
                bank="Bank",
                currency="EURO",
            )

    def test_currency_uppercase(self):
        account = AccountCreate(
            name="Test",
            account_type=AccountType.CORRIENTE,
            bank="Bank",
            currency="eur",
        )
        assert account.currency == "EUR"


class TestAssetSchemas:
    def test_valid_asset_create(self):
        asset = AssetCreate(
            ticker="aapl",
            asset_type=AssetType.STOCK,
            name="Apple",
        )
        assert asset.ticker == "AAPL"

    def test_invalid_ticker_fails(self):
        with pytest.raises(ValidationError):
            AssetCreate(
                ticker="AA PL",
                asset_type=AssetType.STOCK,
                name="Test",
            )


class TestOperationSchemas:
    def test_valid_operation(self):
        op = OperationCreate(
            asset_id=1,
            account_id=1,
            operation_type=OperationType.BUY,
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            operation_date=datetime.utcnow(),
        )
        assert op.total_amount == Decimal("1000")

    def test_zero_quantity_fails(self):
        with pytest.raises(ValidationError):
            OperationCreate(
                asset_id=1,
                account_id=1,
                operation_type=OperationType.BUY,
                quantity=Decimal("0"),
                unit_price=Decimal("100"),
                operation_date=datetime.utcnow(),
            )

    def test_future_date_fails(self):
        from datetime import timedelta

        with pytest.raises(ValidationError):
            OperationCreate(
                asset_id=1,
                account_id=1,
                operation_type=OperationType.BUY,
                quantity=Decimal("10"),
                unit_price=Decimal("100"),
                operation_date=datetime.utcnow() + timedelta(days=1),
            )


class TestPriceSchemas:
    def test_valid_price(self):
        price = PriceCreate(
            asset_id=1,
            price=Decimal("150"),
            price_date=datetime.utcnow(),
        )
        assert price.price == Decimal("150")

    def test_zero_price_fails(self):
        with pytest.raises(ValidationError):
            PriceCreate(
                asset_id=1,
                price=Decimal("0"),
                price_date=datetime.utcnow(),
            )
