"""Funciones helper de uso general."""

from __future__ import annotations

from decimal import Decimal  # noqa: F401
from typing import Any


def safe_divide(
    numerator: Decimal, denominator: Decimal, default: Decimal = Decimal("0")
) -> Decimal:
    """Divide con seguridad; retorna *default* si el denominador es cero."""
    if denominator == 0:
        return default
    return numerator / denominator


def round_decimal(value: Decimal, places: int = 2) -> Decimal:
    """Redondea un Decimal al número de decimales especificado."""
    quantize_val = Decimal(10) ** -places
    return value.quantize(quantize_val)


def format_currency(value: Decimal, currency: str = "EUR") -> str:
    """Formatea un Decimal como moneda legible."""
    symbol_map = {"EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF", "JPY": "¥"}
    symbol = symbol_map.get(currency, currency)
    return f"{symbol} {value:,.2f}"


def paginate(items: list[Any], skip: int = 0, limit: int = 50) -> list[Any]:
    """Aplica paginación *offset/limit* a una lista."""
    return items[skip : skip + limit]
