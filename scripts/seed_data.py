"""Wizard de configuración inicial: pide datos reales del usuario para poblar la BD.

Flujo:
  1. Cuentas corrientes / ahorro / inversión → pide saldo actual
  2. Acciones / ETFs / fondos → pide valor actual y ganancia/pérdida hasta hoy

El script crea automáticamente las operaciones de compra "iniciales" que
reproducen el estado patrimonial declarado por el usuario.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from app.database import SessionLocal, init_db
from app.models.account import Account
from app.models.asset import Asset
from app.models.enums import (
    AccountType,
    AssetType,
    OperationType,
    PriceSource,
)
from app.models.operation import Operation  # noqa: E402
from app.models.price import Price  # noqa: E402

# ─── Helpers de input ────────────────────────────────────────────────


def _prompt(text: str) -> str:
    """Input con prompt limpio."""
    return input(text).strip()


def _prompt_decimal(text: str, allow_zero: bool = False) -> Decimal:
    """Pide un valor decimal válido, reintentando hasta que sea correcto."""
    while True:
        raw = _prompt(text)
        if not raw:
            continue
        try:
            value = Decimal(raw.replace(",", "."))
        except InvalidOperation:
            print("  ⚠️  Valor no válido, intenta de nuevo.")
            continue
        if allow_zero and value == 0:
            return value
        if value < 0:
            print("  ⚠️  El valor no puede ser negativo.")
            continue
        return value


def _prompt_yes_no(text: str) -> bool:
    """Pregunta sí/no."""
    while True:
        raw = _prompt(text + " (s/n): ").lower()
        if raw in {"s", "si", "sí", "y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("  ⚠️  Responde 's' o 'n'.")


def _prompt_choice(text: str, options: dict) -> str:
    """Pide seleccionar una opción de un diccionario ordenado."""
    keys = list(options.keys())
    while True:
        print(text)
        for i, key in enumerate(keys, 1):
            print(f"  {i}. {options[key]}")
        raw = _prompt("Elige una opción (número): ")
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(keys):
                return keys[idx]
        except ValueError:
            pass
        print("  ⚠️  Opción no válida.")


# ─── Paso 1: Cuentas ─────────────────────────────────────────────────

ACCOUNT_TYPES = {
    "Corriente": "Cuenta corriente",
    "Ahorro": "Cuenta de ahorro",
    "Inversión": "Cuenta de inversión",
}

CURRENCIES = {"EUR": "Euro (€)", "USD": "Dollar ($)", "GBP": "Pound (£)"}


def _collect_accounts(db) -> list[Account]:
    """Pide al usuario sus cuentas corrientes con saldo actual."""
    print("\n" + "=" * 60)
    print("  💰  PASO 1: CUENTAS BANCARIAS")
    print("=" * 60)
    print("Vamos a registrar tus cuentas. Para cada una pediremos")
    print("el saldo actual.\n")

    accounts: list[Account] = []

    while True:
        print(f"\n── Cuenta #{len(accounts) + 1} ──")
        name = _prompt("Nombre (ej. Cuenta Corriente BBVA): ")
        if not name:
            print("  ⚠️  El nombre es obligatorio.")
            continue

        account_type = _prompt_choice("Tipo de cuenta:", ACCOUNT_TYPES)
        bank = _prompt("Banco (ej. BBVA, Santander): ")
        if not bank:
            print("  ⚠️  El banco es obligatorio.")
            continue

        iban = _prompt("IBAN (opcional, pulsa Enter para saltar): ")
        currency = _prompt_choice("Moneda:", CURRENCIES)
        balance = _prompt_decimal("Saldo actual: ", allow_zero=True)

        account = Account(
            name=name,
            account_type=AccountType(account_type),
            bank=bank,
            iban=iban or None,
            currency=currency,
            current_balance=balance,
        )
        db.add(account)
        db.flush()
        accounts.append(account)
        print(f"  ✅ Cuenta '{name}' creada con saldo {balance} {currency}")

        if not _prompt_yes_no("\n¿Añadir otra cuenta?"):
            break

    return accounts


# ─── Paso 2: Activos ─────────────────────────────────────────────────

ASSET_TYPES = {
    "Stock": "Acción",
    "ETF": "ETF",
    "Fund": "Fondo de inversión",
    "Crypto": "Criptomoneda",
    "Other": "Otro",
}


def _collect_assets(db, accounts: list[Account]) -> None:
    """Pide activos (acciones, ETFs, fondos) con valor y ganancia/pérdida."""
    print("\n" + "=" * 60)
    print("  📈  PASO 2: ACTIVOS (acciones, ETFs, fondos)")
    print("=" * 60)
    print("Para cada activo pediremos:")
    print("  • Ticker y nombre")
    print("  • Cantidad poseída")
    print("  • Valor actual total")
    print("  • Ganancia o pérdida hasta hoy\n")

    # Si hay varias cuentas, preguntar en cuál registrar los activos
    if not accounts:
        print("  ⚠️  No hay cuentas registradas. Crea una primero.")
        return

    if len(accounts) == 1:
        default_account = accounts[0]
    else:
        print("\n¿En qué cuenta están los activos?")
        for i, acc in enumerate(accounts, 1):
            print(f"  {i}. {acc.name} ({acc.bank})")
        while True:
            raw = _prompt("Elige cuenta (número): ")
            try:
                idx = int(raw) - 1
                if 0 <= idx < len(accounts):
                    default_account = accounts[idx]
                    break
            except ValueError:
                pass
            print("  ⚠️  Opción no válida.")

    while True:
        print(f"\n── Activo #{db.query(Asset).count() + 1} ──")
        ticker = _prompt("Ticker (ej. AAPL, VTI, BTC-USD): ").upper()
        if not ticker:
            print("  ⚠️  El ticker es obligatorio.")
            continue

        name = _prompt("Nombre (ej. Apple Inc.): ")
        if not name:
            name = ticker  # usar ticker como nombre si se deja vacío

        asset_type_str = _prompt_choice("Tipo de activo:", ASSET_TYPES)
        asset_type = AssetType(asset_type_str)
        currency = _prompt_choice("Moneda del activo:", CURRENCIES)

        # ── Datos patrimoniales ──
        quantity = _prompt_decimal("Cantidad poseída (ej. 10, 0.5): ")
        current_value = _prompt_decimal(
            "Valor actual total de la posición (ej. 1500.00): "
        )

        # Ganancia/pérdida
        print("\n  ¿Tienes ganancia o pérdida hasta hoy?")
        has_gain = _prompt_yes_no("  ¿Hay ganancia (s) o pérdida (n)?")
        gain_loss = _prompt_decimal("  ¿Cuánto? (importe total): ")
        if not has_gain:
            gain_loss = -gain_loss

        # ── Calcular precio unitario y costo de compra ──
        # valor_actual = cantidad * precio_actual → precio_actual = valor/cantidad
        if quantity > 0:
            current_price = current_value / quantity
        else:
            current_price = Decimal("0")

        # costo_compra = valor_actual - ganancia
        cost_basis = current_value - gain_loss
        if cost_basis < 0:
            cost_basis = Decimal("0")

        # precio de compra unitario
        if quantity > 0:
            unit_price = cost_basis / quantity
        else:
            unit_price = Decimal("0")

        # ── Crear el asset ──
        asset = Asset(
            ticker=ticker,
            asset_type=asset_type,
            name=name,
            currency=currency,
            current_price=current_price,
            manual_price=True,
            price_updated_at=datetime.utcnow(),
        )
        db.add(asset)
        db.flush()

        # ── Crear operación de compra inicial ──
        # Esta operación sintética reproduce el estado actual declarado.
        total_amount = unit_price * quantity

        op = Operation(
            asset_id=asset.id,
            account_id=default_account.id,
            operation_type=OperationType.BUY,
            quantity=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            commission=Decimal("0"),
            operation_date=datetime.utcnow() - timedelta(days=365),
            notes=f"Saldo inicial — valor actual {current_value} {currency}, "
            f"ganancia/pérdida {gain_loss} {currency}",
        )
        db.add(op)
        db.flush()

        # ── Guardar el precio actual en el histórico ──
        price = Price(
            asset_id=asset.id,
            price=current_price,
            price_date=datetime.utcnow(),
            source=PriceSource.MANUAL,
        )
        db.add(price)
        db.flush()

        gain_str = f"+{gain_loss}" if gain_loss >= 0 else str(gain_loss)
        print(f"  ✅ Activo '{ticker}' creado:")
        print(f"     Cantidad: {quantity}")
        print(f"     Precio actual: {current_price:.4f} {currency}")
        print(f"     Valor actual: {current_value} {currency}")
        print(f"     Costo de compra: {cost_basis} {currency}")
        print(f"     Ganancia/Pérdida: {gain_str} {currency}")
        print(f"     Cuenta asociada: {default_account.name}")

        if not _prompt_yes_no("\n¿Añadir otro activo?"):
            break


# ─── Main ────────────────────────────────────────────────────────────


def seed_data() -> None:
    """Wizard interactivo para poblar la BD con datos reales del usuario."""
    init_db()

    db = SessionLocal()

    # Verificar si ya hay datos
    if db.query(Account).count() > 0:
        if not _prompt_yes_no("ℹ️  La BD ya contiene datos. ¿Continuar y añadir más?"):
            print("Operación cancelada.")
            db.close()
            return

    print("\n" + "=" * 60)
    print("  🎯  CONFIGURACIÓN INICIAL DE PATRIMONIA")
    print("=" * 60)
    print("Este wizard te guiará para registrar tu patrimonio actual.")
    print("Puedes interrumpir con Ctrl+C en cualquier momento.\n")

    try:
        # Paso 1: Cuentas
        accounts = _collect_accounts(db)

        if not accounts:
            print("\n⚠️  No se registraron cuentas. Creando cuenta por defecto...")
            account = Account(
                name="Cuenta Principal",
                account_type=AccountType.CORRIENTE,
                bank="Manual",
                currency="EUR",
                current_balance=Decimal("0"),
            )
            db.add(account)
            db.flush()
            accounts = [account]

        # Paso 2: Activos
        _collect_assets(db, accounts)

        db.commit()

        # Resumen
        print("\n" + "=" * 60)
        print("  📊  RESUMEN DE DATOS CARGADOS")
        print("=" * 60)
        n_accounts = db.query(Account).count()
        n_assets = db.query(Asset).count()
        n_ops = db.query(Operation).count()
        n_prices = db.query(Price).count()
        print(f"  • Cuentas:   {n_accounts}")
        print(f"  • Activos:   {n_assets}")
        print(f"  • Operaciones: {n_ops}")
        print(f"  • Precios:   {n_prices}")
        print("=" * 60)
        print("✅ ¡Configuración completada!")
        print(f"   Base de datos: SQLite en {Path('patrimonio.db').resolve()}")
        print("   Ejecuta 'make run' para iniciar la aplicación.\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Operación interrumpida. Cambios no guardados.")
        db.rollback()
    except Exception as exc:
        print(f"\n❌ Error: {exc}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
