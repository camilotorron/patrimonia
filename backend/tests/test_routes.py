"""Tests de integración para las rutas de la API."""

from __future__ import annotations

from decimal import Decimal


class TestAccountsRoutes:
    def test_list_accounts_empty(self, client):
        response = client.get("/api/v1/accounts")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_account(self, client):
        response = client.post(
            "/api/v1/accounts",
            json={
                "name": "Test Account API",
                "account_type": "Corriente",
                "bank": "Test Bank",
                "currency": "EUR",
                "current_balance": "5000",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Account API"
        assert data["id"] is not None

    def test_create_duplicate_account(self, client):
        payload = {
            "name": "Dup API",
            "account_type": "Corriente",
            "bank": "Bank",
            "currency": "EUR",
        }
        client.post("/api/v1/accounts", json=payload)
        response = client.post("/api/v1/accounts", json=payload)
        assert response.status_code == 409

    def test_get_account_not_found(self, client):
        response = client.get("/api/v1/accounts/99999")
        assert response.status_code == 404

    def test_get_account_by_id(self, client):
        create_resp = client.post(
            "/api/v1/accounts",
            json={
                "name": "Get Test",
                "account_type": "Corriente",
                "bank": "Bank",
                "currency": "EUR",
            },
        )
        account_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Get Test"

    def test_update_account(self, client):
        create_resp = client.post(
            "/api/v1/accounts",
            json={
                "name": "Update Me",
                "account_type": "Corriente",
                "bank": "Bank",
                "currency": "EUR",
            },
        )
        account_id = create_resp.json()["id"]
        response = client.put(
            f"/api/v1/accounts/{account_id}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_delete_account(self, client):
        create_resp = client.post(
            "/api/v1/accounts",
            json={
                "name": "Delete Me",
                "account_type": "Corriente",
                "bank": "Bank",
                "currency": "EUR",
            },
        )
        account_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 204

    def test_get_account_balance(self, client):
        create_resp = client.post(
            "/api/v1/accounts",
            json={
                "name": "Balance Test",
                "account_type": "Corriente",
                "bank": "Bank",
                "currency": "EUR",
                "current_balance": "7500",
            },
        )
        account_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/accounts/{account_id}/balance")
        assert response.status_code == 200
        assert "balance" in response.json()


class TestAssetsRoutes:
    def test_list_assets_empty(self, client):
        response = client.get("/api/v1/assets")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_asset(self, client):
        response = client.post(
            "/api/v1/assets",
            json={
                "ticker": "MSFT",
                "asset_type": "Stock",
                "name": "Microsoft Corp",
                "currency": "USD",
            },
        )
        assert response.status_code == 201
        assert response.json()["ticker"] == "MSFT"

    def test_get_asset_not_found(self, client):
        response = client.get("/api/v1/assets/99999")
        assert response.status_code == 404

    def test_search_assets(self, client):
        client.post(
            "/api/v1/assets",
            json={
                "ticker": "TSLA",
                "asset_type": "Stock",
                "name": "Tesla Inc",
                "currency": "USD",
            },
        )
        response = client.get("/api/v1/assets/search?query=TSLA")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_asset_holdings(self, client, db_session, sample_account, sample_asset):
        from app.services.operation_service import OperationService

        op_service = OperationService(db_session)
        op_service.create_buy_operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            quantity=Decimal("10"),
            unit_price=Decimal("150"),
        )
        db_session.commit()

        response = client.get(f"/api/v1/assets/{sample_asset.id}/holdings")
        assert response.status_code == 200
        data = response.json()
        assert "quantity" in data
        assert "current_value" in data


class TestOperationsRoutes:
    def test_list_operations_empty(self, client):
        response = client.get("/api/v1/operations")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_buy_operation(
        self, client, db_session, sample_account, sample_asset
    ):
        from datetime import datetime

        response = client.post(
            "/api/v1/operations",
            json={
                "asset_id": sample_asset.id,
                "account_id": sample_account.id,
                "operation_type": "Buy",
                "quantity": "10",
                "unit_price": "150",
                "commission": "5",
                "operation_date": datetime.utcnow().isoformat(),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["operation_type"] == "Buy"

    def test_create_operation_invalid_quantity(
        self, client, sample_account, sample_asset
    ):
        from datetime import datetime

        response = client.post(
            "/api/v1/operations",
            json={
                "asset_id": sample_asset.id,
                "account_id": sample_account.id,
                "operation_type": "Buy",
                "quantity": "-5",
                "unit_price": "150",
                "operation_date": datetime.utcnow().isoformat(),
            },
        )
        assert response.status_code == 422

    def test_delete_operation(self, client, db_session, sample_account, sample_asset):
        from datetime import datetime

        from app.services.operation_service import OperationService

        op_service = OperationService(db_session)
        op = op_service.create_buy_operation(
            asset_id=sample_asset.id,
            account_id=sample_account.id,
            quantity=Decimal("5"),
            unit_price=Decimal("100"),
        )
        db_session.commit()

        response = client.delete(f"/api/v1/operations/{op.id}")
        assert response.status_code == 204


class TestReportsRoutes:
    def test_get_summary(self, client):
        response = client.get("/api/v1/reports/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_wealth" in data
        assert "portfolio_value" in data

    def test_get_composition(self, client):
        response = client.get("/api/v1/reports/composition")
        assert response.status_code == 200
        data = response.json()
        assert "by_type" in data
        assert "by_account" in data

    def test_get_returns(self, client):
        response = client.get("/api/v1/reports/returns")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_get_history(self, client):
        response = client.get("/api/v1/reports/history")
        assert response.status_code == 200
        data = response.json()
        assert "points" in data


class TestHealthRoutes:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_version(self, client):
        response = client.get("/version")
        assert response.status_code == 200
        assert "version" in response.json()
