"""Importa datos iniciales desde archivos JSON en init_data/ a la base de datos.

Lee:
  - accounts.json  → cuentas bancarias con saldo actual
  - stock.json     → acciones con valor actual y ganancia/pérdida
  - etfs.json      → ETFs con valor actual y ganancia/pérdida
  - funds.json     → fondos con valor actual y ganancia/pérdida

Para cada activo crea:
  - El registro del activo (Asset) con precio actual manual
  - Una operación de compra inicial que reproduce el estado declarado
  - Un registro de precio en el histórico
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from app.config import settings
from app.database import SessionLocal, drop_db, init_db
from app.models.account import Account
from app.models.account_balance import AccountBalance
from app.models.asset import Asset
from app.models.enums import (
    AccountType,
    AssetType,
    OperationType,
    PriceSource,
)
from app.models.operation import Operation
from app.models.price import Price

DATA_DIR = settings.init_data_dir


def _load_json(filename: str) -> list[dict]:
    """Carga un archivo JSON del directorio de datos iniciales."""
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  ⚠️  No existe {path}, saltando...")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _parse_date(date_str: str | None) -> datetime:
    """Parsea una fecha ISO o retorna UTC now."""
    if date_str:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return datetime.utcnow()


def import_accounts(db) -> dict[str, Account]:
    """Importa las cuentas desde accounts.json. Retorna dict bank_name → Account."""
    data = _load_json("accounts.json")
    if not data:
        return {}

    print(f"\n  📂 Importando {len(data)} cuentas...")
    accounts_by_name: dict[str, Account] = {}

    for item in data:
        bank = item["bank_name"]
        balance = Decimal(str(item["current_balance"]))

        # Nombre único: si hay duplicados, añadir sufijo
        name = f"Cuenta {bank}"
        if name in accounts_by_name:
            name = f"Cuenta {bank} ({len(accounts_by_name)})"

        account = Account(
            name=name,
            account_type=AccountType.CORRIENTE,
            bank=bank,
            currency="EUR",
            current_balance=balance,
        )
        db.add(account)
        db.flush()
        accounts_by_name[bank] = account

        # Registrar el saldo inicial con fecha 2024-01-01 para la gráfica de evolución
        initial_date = datetime(2024, 1, 1)
        balance_record = AccountBalance(
            account_id=account.id,
            balance=balance,
            recorded_at=initial_date,
        )
        db.add(balance_record)
        db.flush()

        print(f"    ✅ {name} — saldo: {balance} EUR (registro inicial 2024-01-01)")

    return accounts_by_name


def import_assets(
    db,
    accounts: dict[str, Account],
    filename: str,
    asset_type: AssetType,
) -> None:
    """Importa activos (stocks/ETFs/funds) desde un archivo JSON."""
    data = _load_json(filename)
    if not data:
        return

    type_label = {
        AssetType.STOCK: "acciones",
        AssetType.ETF: "ETFs",
        AssetType.FUND: "fondos",
    }.get(asset_type, "activos")

    print(f"\n  📂 Importando {len(data)} {type_label}...")

    for item in data:
        bank = item["bank_name"]
        name = (
            item.get("stock_name")
            or item.get("etf_name")
            or item.get("fund_name")
            or "Unknown"
        )
        isin = item.get("isin", "")
        units = Decimal(str(item["units"]))
        total_value = Decimal(str(item["total_value"]))
        revenue = Decimal(str(item.get("initial_revenue", "0")))
        date = _parse_date(item.get("date"))

        # Buscar la cuenta asociada; si no existe, usar la primera
        account = accounts.get(bank)
        if account is None:
            account = next(iter(accounts.values()))

        # Calcular precios
        current_price = total_value / units if units > 0 else Decimal("0")
        cost_basis = total_value - revenue
        unit_price = cost_basis / units if units > 0 else Decimal("0")
        total_amount = unit_price * units

        # Usar el ISIN como ticker (identificador único)
        ticker = isin or name[:20].upper()

        # Crear el activo
        asset = Asset(
            ticker=ticker,
            asset_type=asset_type,
            name=name,
            currency="EUR",
            current_price=current_price,
            manual_price=True,
            price_updated_at=date,
        )
        db.add(asset)
        db.flush()

        # Crear operación de compra inicial
        op = Operation(
            asset_id=asset.id,
            account_id=account.id,
            operation_type=OperationType.BUY,
            quantity=units,
            unit_price=unit_price,
            total_amount=total_amount,
            commission=Decimal("0"),
            operation_date=date,
            notes=f"Saldo inicial — valor actual {total_value} EUR, ganancia/pérdida {revenue} EUR",
        )
        db.add(op)
        db.flush()

        # Guardar precio actual en histórico
        price = Price(
            asset_id=asset.id,
            price=current_price,
            price_date=date,
            source=PriceSource.MANUAL,
        )
        db.add(price)
        db.flush()

        gain_str = f"+{revenue}" if revenue >= 0 else str(revenue)
        print(
            f"    ✅ {name} ({ticker}) — valor: {total_value} EUR, ganancia: {gain_str} EUR"
        )


def import_initial_data() -> None:
    """Punto de entrada: borra la BD, la recrea y la puebla desde JSON."""
    print("\n" + "=" * 60)
    print("  🚀  IMPORTACIÓN DE DATOS INICIALES")
    print("=" * 60)
    print(f"  Directorio de datos: {DATA_DIR}")

    if not DATA_DIR.exists():
        print(f"  ❌ No existe el directorio {DATA_DIR}")
        print("     Crea la carpeta 'init_data/' con tus archivos JSON.")
        return

    # Reset completo de la BD
    print("\n  🧹 Borrando base de datos anterior...")
    drop_db()
    init_db()
    print("  ✅ Base de datos recreada")

    db = SessionLocal()

    try:
        # 1. Cuentas
        accounts = import_accounts(db)
        if not accounts:
            print("\n  ❌ No se encontraron cuentas. Abortando.")
            return

        # 2. Acciones
        import_assets(db, accounts, "stock.json", AssetType.STOCK)

        # 3. ETFs
        import_assets(db, accounts, "etfs.json", AssetType.ETF)

        # 4. Fondos
        import_assets(db, accounts, "funds.json", AssetType.FUND)

        db.commit()

        # Resumen
        n_accounts = db.query(Account).count()
        n_assets = db.query(Asset).count()
        n_ops = db.query(Operation).count()
        n_prices = db.query(Price).count()

        print("\n" + "=" * 60)
        print("  📊  RESUMEN")
        print("=" * 60)
        print(f"  • Cuentas:     {n_accounts}")
        print(f"  • Activos:     {n_assets}")
        print(f"  • Operaciones: {n_ops}")
        print(f"  • Precios:     {n_prices}")
        print("=" * 60)
        print("✅ ¡Importación completada!\n")

    except Exception as exc:
        db.rollback()
        print(f"\n❌ Error durante la importación: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import_initial_data()
