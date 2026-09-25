"""Constantes compartidas por toda la aplicación."""

from __future__ import annotations

from decimal import Decimal

# Versiones e identificadores
API_V1_PREFIX = "/api/v1"

# Decimales
ZERO = Decimal("0")
PRECISION_PRICE = Decimal("0.000001")
PRECISION_QUANTITY = Decimal("0.00000001")

# Monedas
DEFAULT_CURRENCY = "EUR"
SUPPORTED_CURRENCIES = {"EUR", "USD", "GBP", "CHF", "JPY"}

# Cache TTL defaults (segundos)
DEFAULT_CACHE_TTL = 3600
