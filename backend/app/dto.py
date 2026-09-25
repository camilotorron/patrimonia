"""Dataclasses usados como DTOs internos entre la capa de servicios y rutas.

Los DTOs no dependen de Pydantic y son tipos Python puros, lo que facilita
el testeo y separa la lógica de negocio del transporte (HTTP).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class HoldingsDTO:
    """Posición actual de un activo."""

    asset_id: int
    ticker: str
    quantity: Decimal
    average_price: Decimal
    total_invested: Decimal
    current_value: Decimal
    gain: Decimal
    gain_percentage: Decimal


@dataclass(frozen=True)
class ReturnDTO:
    """Rentabilidad de un activo (realizada + no realizada)."""

    asset_id: int
    ticker: str
    realized_gain: Decimal
    unrealized_gain: Decimal
    total_gain: Decimal
    return_percentage: Decimal


@dataclass(frozen=True)
class AccountSummaryDTO:
    """Resumen financiero de una cuenta."""

    account_id: int
    balance: Decimal
    assets_value: Decimal
    total: Decimal
    currencies: dict[str, Decimal] = field(default_factory=dict)


@dataclass(frozen=True)
class AssetSnapshotDTO:
    """Snapshot de un activo con datos actuales."""

    asset_id: int
    ticker: str
    name: str
    asset_type: str
    current_price: Decimal | None
    quantity: Decimal
    current_value: Decimal
    cost_basis: Decimal
    gain: Decimal
    gain_percentage: Decimal


@dataclass(frozen=True)
class PortfolioValueDTO:
    """Valor del portafolio de una cuenta o total."""

    total_invested: Decimal
    current_value: Decimal
    gain: Decimal
    gain_percentage: Decimal


@dataclass(frozen=True)
class PriceRefreshResultDTO:
    """Resultado de actualizar el precio de un activo."""

    asset_id: int
    ticker: str
    old_price: Decimal | None
    new_price: Decimal
    timestamp: datetime
    success: bool = True
    error: str | None = None


@dataclass(frozen=True)
class BulkRefreshResultDTO:
    """Resultado de actualizar precios de múltiples activos."""

    updated: list[PriceRefreshResultDTO]
    failed: list[PriceRefreshResultDTO]

    @property
    def updated_count(self) -> int:
        return len(self.updated)

    @property
    def failed_count(self) -> int:
        return len(self.failed)
