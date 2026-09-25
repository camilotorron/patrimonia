"""Proveedor de precios usando yfinance."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


class PriceProvider(ABC):
    """Interfaz abstracta para proveedores de precios."""

    @abstractmethod
    def get_price(self, ticker: str) -> Decimal | None:
        """Obtiene el precio actual de un ticker."""

    @abstractmethod
    def get_prices(self, tickers: list[str]) -> dict[str, Decimal]:
        """Obtiene precios de múltiples tickers."""

    @abstractmethod
    def get_info(self, ticker: str) -> dict[str, Any]:
        """Obtiene información de un ticker."""

    @abstractmethod
    def validate_ticker(self, ticker: str) -> bool:
        """Verifica si un ticker existe."""


class YFinancePriceProvider(PriceProvider):
    """Implementación de proveedor de precios usando yfinance."""

    def __init__(self) -> None:
        try:
            import yfinance as yf  # noqa: PLC0415

            self._yf = yf
        except ImportError:
            logger.warning("yfinance not installed")
            self._yf = None

    def _ensure_available(self) -> None:
        if self._yf is None:
            raise RuntimeError("yfinance is not installed")

    # ------------------------------------------------------------------ #
    # Implementación de la interfaz
    # ------------------------------------------------------------------ #
    def get_price(self, ticker: str) -> Decimal | None:
        """Obtiene el precio actual de un ticker."""
        self._ensure_available()
        try:
            info = self._yf.Ticker(ticker).fast_info
            price = info.get("last_price") or info.get("lastPrice")
            if price is not None:
                return Decimal(str(price))
        except Exception:
            logger.exception("Failed to fetch price for %s", ticker)
        return None

    def get_prices(self, tickers: list[str]) -> dict[str, Decimal]:
        """Obtiene precios de múltiples tickers en batch."""
        self._ensure_available()
        result: dict[str, Decimal] = {}
        for ticker in tickers:
            price = self.get_price(ticker)
            if price is not None:
                result[ticker] = price
        return result

    def get_info(self, ticker: str) -> dict[str, Any]:
        """Obtiene información extendida de un ticker."""
        self._ensure_available()
        try:
            t = self._yf.Ticker(ticker)
            info = t.info
            return {
                "name": info.get("shortName") or info.get("longName"),
                "currency": info.get("currency"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
            }
        except Exception:
            logger.exception("Failed to fetch info for %s", ticker)
            return {}

    def validate_ticker(self, ticker: str) -> bool:
        """Verifica si un ticker existe en yfinance."""
        self._ensure_available()
        try:
            info = self._yf.Ticker(ticker).fast_info
            return (
                info.get("last_price") is not None or info.get("lastPrice") is not None
            )
        except Exception:
            return False

    def search_ticker(self, query: str) -> list[dict[str, Any]]:
        """Busca tickers que coincidan con el query."""
        self._ensure_available()
        try:
            results = self._yf.Search(query).quotes
            return [
                {
                    "symbol": r.get("symbol"),
                    "name": r.get("shortname") or r.get("longname"),
                    "exchange": r.get("exchange"),
                    "type": r.get("quoteType"),
                }
                for r in results[:10]
            ]
        except Exception:
            logger.exception("Ticker search failed for query '%s'", query)
            return []
