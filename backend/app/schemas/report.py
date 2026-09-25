"""Schemas de Pydantic para reportes y analytics."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class ReportPeriod(str, Enum):
    """Períodos de reporte."""

    ALL = "all"
    YEAR = "year"
    QUARTER = "quarter"
    MONTH = "month"


class PortfolioSummary(BaseModel):
    """Resumen del portafolio."""

    total_wealth: Decimal
    total_invested: Decimal
    total_gain: Decimal
    total_gain_percentage: Decimal
    portfolio_value: Decimal
    cash: Decimal
    by_currency: dict[str, dict[str, Decimal]]
    last_updated: datetime | None


class CompositionItem(BaseModel):
    """Item de composición del portafolio."""

    type: str
    value: Decimal
    percentage: Decimal


class CompositionReport(BaseModel):
    """Reporte de composición."""

    by_type: list[CompositionItem]
    by_account: list[CompositionItem]


class ReturnItem(BaseModel):
    """Rentabilidad de un activo."""

    asset_id: int
    ticker: str
    name: str
    quantity: Decimal
    cost_basis: Decimal
    current_value: Decimal
    unrealized_gain: Decimal
    realized_gain: Decimal
    total_gain: Decimal
    return_percentage: Decimal


class ReturnReport(BaseModel):
    """Reporte de rentabilidad."""

    items: list[ReturnItem]
    total_return: Decimal
    total_return_percentage: Decimal


class HistoryPoint(BaseModel):
    """Punto en el histórico de patrimonio."""

    date: datetime
    total_value: Decimal
    change: Decimal | None
    change_percentage: Decimal | None


class HistoryReport(BaseModel):
    """Reporte histórico de patrimonio."""

    points: list[HistoryPoint]
    max_value: Decimal | None
    min_value: Decimal | None
    avg_value: Decimal | None
