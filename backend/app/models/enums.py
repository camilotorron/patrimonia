"""Enumeraciones compartidas por toda la aplicación."""

from __future__ import annotations

from enum import Enum


class AccountType(str, Enum):
    """Tipos de cuenta soportados."""

    CORRIENTE = "Corriente"
    AHORRO = "Ahorro"
    INVERSION = "Inversión"


class AssetType(str, Enum):
    """Tipos de activo financiero."""

    STOCK = "Stock"
    ETF = "ETF"
    FUND = "Fund"
    CRYPTO = "Crypto"
    OTHER = "Other"


class OperationType(str, Enum):
    """Tipos de operación sobre un activo."""

    BUY = "Buy"
    SELL = "Sell"


class PriceSource(str, Enum):
    """Origen del precio de un activo."""

    YFINANCE = "yfinance"
    MANUAL = "manual"
    API = "api"
