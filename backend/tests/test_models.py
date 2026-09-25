"""Tests para los modelos SQLAlchemy."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from app.models.account import Account
from app.models.asset import Asset
from app.models.enums import AccountType, AssetType, OperationType, PriceSource
from app.models.operation import Operation
from app.models.price import Price


class TestAccountModel:
    def test_create_account(self, db_session):
        account = Account(
            name="Test Account",
            account_type=AccountType.CORRIENTE,
            bank="Test Bank",
            currency="EUR",
            current_balance=Decimal("1000"),
        )
        db_session.add(account)
        db_session.commit()

        assert account.id is not None
        assert account.name == "Test Account"
        assert account.account_type == AccountType.CORRIENTE
        assert account.is_active is True
        assert account.created_at is not None
        assert account.updated_at is not None

    def test_account_default_currency(self, db_session):
        account = Account(
            name="EUR Account",
            account_type=AccountType.AHORRO,
            bank="Bank",
        )
        db_session.add(account)
        db_session.commit()
        assert account.currency == "EUR"

    def test_account_repr(self, db_session):
        account = Account(name="A", account_type=AccountType.CORRIENTE, bank="B")
        db_session.add(account)
        db_session.commit()
        assert "Account" in repr(account)
        assert str(account.id) in repr(account)


class TestAssetModel:
    def test_create_asset(self, db_session):
        asset = Asset(
            ticker="AAPL",
            asset_type=AssetType.STOCK,
            name="Apple Inc.",
        )
        db_session.add(asset)
        db_session.commit()

        assert asset.id is not None
        assert asset.ticker == "AAPL"
        assert asset.is_active is True
        assert asset.manual_price is False
        assert asset.current_price is None

    def test_asset_with_price(self, db_session):
        asset = Asset(
            ticker="VTI",
            asset_type=AssetType.ETF,
            name="Vanguard Total Market",
            current_price=Decimal("220.50"),
        )
        db_session.add(asset)
        db_session.commit()
        assert asset.current_price == Decimal("220.50")


class TestOperationModel:
    def test_create_buy_operation(self, db_session, sample_account, sample_asset):
        op = Operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            operation_type=OperationType.BUY,
            quantity=Decimal("10"),
            unit_price=Decimal("150"),
            total_amount=Decimal("1505"),
            commission=Decimal("5"),
            operation_date=datetime.utcnow(),
        )
        db_session.add(op)
        db_session.commit()

        assert op.id is not None
        assert op.operation_type == OperationType.BUY
        assert op.quantity == Decimal("10")

    def test_operation_relationships(self, db_session, sample_account, sample_asset):
        op = Operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            operation_type=OperationType.BUY,
            quantity=Decimal("5"),
            unit_price=Decimal("100"),
            total_amount=Decimal("500"),
            operation_date=datetime.utcnow(),
        )
        db_session.add(op)
        db_session.commit()

        assert op.asset.ticker == "AAPL"
        assert op.account.name == "Cuenta Test"


class TestPriceModel:
    def test_create_price(self, db_session, sample_asset):
        price = Price(
            asset_id=sample_asset.id,
            price=Decimal("155.50"),
            price_date=datetime.utcnow(),
            source=PriceSource.YFINANCE,
        )
        db_session.add(price)
        db_session.commit()

        assert price.id is not None
        assert price.price == Decimal("155.50")
        assert price.source == PriceSource.YFINANCE
