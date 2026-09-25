"""Fixtures de pytest compartidas por todos los tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models.enums import AccountType, AssetType, OperationType
from app.models.account import Account
from app.models.asset import Asset
from app.models.operation import Operation


# ------------------------------------------------------------------ #
# Database fixtures
# ------------------------------------------------------------------ #
@pytest.fixture()
def db_engine():
    """Engine de SQLite en memoria para tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(db_engine):
    """Sesión de BD para tests."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    """Cliente de prueba de FastAPI con BD inyectada."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# ------------------------------------------------------------------ #
# Data fixtures
# ------------------------------------------------------------------ #
@pytest.fixture()
def sample_account(db_session):
    """Crea una cuenta de prueba."""
    account = Account(
        name="Cuenta Test",
        account_type=AccountType.CORRIENTE,
        bank="Banco Test",
        currency="EUR",
        current_balance=10000,
    )
    db_session.add(account)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture()
def sample_asset(db_session):
    """Crea un activo de prueba."""
    asset = Asset(
        ticker="AAPL",
        asset_type=AssetType.STOCK,
        name="Apple Inc.",
        currency="USD",
        current_price=150,
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset


@pytest.fixture()
def sample_operation(db_session, sample_account, sample_asset):
    """Crea una operación de compra de prueba."""
    from decimal import Decimal
    from datetime import datetime

    op = Operation(
        asset_id=sample_asset.id,
        account_id=sample_account.id,
        operation_type=OperationType.BUY,
        quantity=Decimal("10"),
        unit_price=Decimal("150"),
        total_amount=Decimal("1500"),
        commission=Decimal("5"),
        operation_date=datetime.utcnow(),
    )
    db_session.add(op)
    db_session.commit()
    db_session.refresh(op)
    return op
