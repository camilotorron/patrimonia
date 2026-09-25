"""Tests para el importador CSV."""

from __future__ import annotations

from decimal import Decimal

from app.services.csv_importer import CSVImporter

SAMPLE_CSV = """date,operation_type,account,asset_ticker,quantity,unit_price,commission,notes
2024-01-15,Buy,Cuenta 1,AAPL,10,150.50,9.99,"Compra inicial"
2024-02-20,Buy,Cuenta 1,VTI,5,200.00,0,"ETF"
2024-03-10,Sell,Cuenta 1,AAPL,5,160.00,9.99,"Venta parcial"
"""

BAD_CSV = """date,operation_type,account,asset_ticker,quantity,unit_price,commission,notes
2024-01-15,Buy,Cuenta 1,AAPL,INVALID,150.50,9.99,"Bad row"
"""


class TestCSVImporter:
    def test_parse_valid_csv(self, db_session):
        importer = CSVImporter(db_session)
        rows = importer.parse_csv(SAMPLE_CSV)
        assert len(rows) == 3
        assert rows[0]["asset_ticker"] == "AAPL"
        assert rows[1]["operation_type"].value == "Buy"
        assert rows[2]["operation_type"].value == "Sell"

    def test_parse_bad_csv_row(self, db_session):
        importer = CSVImporter(db_session)
        rows = importer.parse_csv(BAD_CSV)
        assert len(rows) == 1
        assert rows[0].get("_error") is True

    def test_parse_missing_headers(self, db_session):
        bad_content = "foo,bar\n1,2\n"
        importer = CSVImporter(db_session)
        try:
            importer.parse_csv(bad_content)
            assert False, "Should have raised"
        except ValueError as e:
            assert "Missing CSV headers" in str(e)

    def test_import_operations(self, db_session, sample_account, sample_asset):
        # Crear segundo asset para el CSV
        from app.models.asset import Asset
        from app.models.enums import AssetType

        vti = Asset(
            ticker="VTI",
            asset_type=AssetType.ETF,
            name="Vanguard Total Market",
            currency="USD",
        )
        db_session.add(vti)
        db_session.commit()

        csv_content = f"""date,operation_type,account,asset_ticker,quantity,unit_price,commission,notes
2024-01-15,Buy,Cuenta 1,AAPL,10,150.00,5,"Compra"
2024-02-20,Buy,Cuenta 1,VTI,5,200.00,0,"ETF"
"""
        importer = CSVImporter(db_session)
        result = importer.import_operations(
            csv_content,
            account_id_map={"Cuenta 1": sample_account.id},
            asset_id_map={"AAPL": sample_asset.id, "VTI": vti.id},
        )
        assert result["imported"] == 2
        assert len(result["errors"]) == 0
