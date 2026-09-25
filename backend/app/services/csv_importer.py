"""Importador de operaciones desde CSV."""

from __future__ import annotations

import csv
import io
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import OperationType
from app.services.operation_service import OperationService

logger = logging.getLogger(__name__)

EXPECTED_HEADERS = [
    "date",
    "operation_type",
    "account",
    "asset_ticker",
    "quantity",
    "unit_price",
    "commission",
    "notes",
]


class CSVImporter:
    """Parser e importador de operaciones desde CSV."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.operation_service = OperationService(db)

    def parse_csv(self, content: str) -> list[dict[str, Any]]:
        """Parsea el contenido CSV en una lista de diccionarios."""
        reader = csv.DictReader(io.StringIO(content))

        # Validar headers
        missing = set(EXPECTED_HEADERS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV headers: {missing}")

        rows: list[dict[str, Any]] = []
        for i, row in enumerate(reader, start=2):  # line 1 is header
            try:
                parsed = {
                    "date": datetime.strptime(row["date"], "%Y-%m-%d"),
                    "operation_type": OperationType(row["operation_type"]),
                    "account": row["account"],
                    "asset_ticker": row["asset_ticker"],
                    "quantity": Decimal(row["quantity"]),
                    "unit_price": Decimal(row["unit_price"]),
                    "commission": Decimal(row.get("commission") or "0"),
                    "notes": row.get("notes") or None,
                }
                rows.append(parsed)
            except Exception:
                logger.exception("Error parsing CSV row %d", i)
                rows.append(
                    {
                        "_error": True,
                        "row": i,
                        "raw": row,
                    }
                )
        return rows

    def import_operations(
        self, content: str, account_id_map: dict[str, int], asset_id_map: dict[str, int]
    ) -> dict[str, Any]:
        """Importa operaciones desde CSV.

        ``account_id_map`` y ``asset_id_map`` mapean nombres/tickers a IDs.
        """
        rows = self.parse_csv(content)
        imported = 0
        errors: list[str] = []

        for row in rows:
            if row.get("_error"):
                errors.append(f"Row {row['row']}: parse error")
                continue

            account_id = account_id_map.get(row["account"])
            asset_id = asset_id_map.get(row["asset_ticker"])

            if account_id is None:
                errors.append(f"Account '{row['account']}' not found")
                continue
            if asset_id is None:
                errors.append(f"Asset '{row['asset_ticker']}' not found")
                continue

            try:
                if row["operation_type"] == OperationType.BUY:
                    self.operation_service.create_buy_operation(
                        asset_id=asset_id,
                        account_id=account_id,
                        quantity=row["quantity"],
                        unit_price=row["unit_price"],
                        commission=row["commission"],
                        operation_date=row["date"],
                        notes=row["notes"],
                    )
                else:
                    self.operation_service.create_sell_operation(
                        asset_id=asset_id,
                        account_id=account_id,
                        quantity=row["quantity"],
                        unit_price=row["unit_price"],
                        commission=row["commission"],
                        operation_date=row["date"],
                        notes=row["notes"],
                    )
                imported += 1
            except Exception:
                logger.exception("Import error for row")
                errors.append(f"Row with {row['asset_ticker']}: operation failed")

        self.db.commit()
        return {"imported": imported, "errors": errors}
