"""Rutas API para reportes y analytics."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.report import ReportPeriod
from app.services.calculation_service import CalculationService

router = APIRouter()


@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)):
    """Resumen completo del portafolio."""
    calc = CalculationService(db)
    wealth = calc.calculate_total_wealth()
    portfolio = calc.calculate_portfolio_value()

    # Calcular efectivo
    accounts = calc.account_repo.get_active()
    cash = sum((a.current_balance for a in accounts), Decimal("0"))  # noqa: F821

    gain = portfolio.gain
    gain_pct = portfolio.gain_percentage

    return {
        "total_wealth": wealth,
        "total_invested": portfolio.total_invested,
        "total_gain": gain,
        "total_gain_percentage": gain_pct,
        "portfolio_value": portfolio.current_value,
        "cash": cash,
        "by_currency": {
            "EUR": {"value": wealth, "invested": portfolio.total_invested, "gain": gain}
        },
        "last_updated": datetime.utcnow(),
    }


@router.get("/composition")
async def get_composition(db: Session = Depends(get_db)):
    """Composición del portafolio por tipo de activo y por cuenta."""
    calc = CalculationService(db)

    by_type = calc.calculate_portfolio_composition()

    # Composición por cuenta
    accounts = calc.account_repo.get_active()
    by_account = []
    total = calc.calculate_total_wealth()
    for account in accounts:
        summary = calc.get_account_summary(account.id)
        by_account.append(
            {
                "type": account.name,
                "value": summary.total,
                "percentage": (summary.total / total * 100) if total > 0 else 0,
            }
        )

    return {"by_type": by_type, "by_account": by_account}


@router.get("/returns")
async def get_returns(
    period: ReportPeriod = Query(ReportPeriod.ALL), db: Session = Depends(get_db)
):
    """Rentabilidad por activo."""
    calc = CalculationService(db)
    assets = calc.asset_repo.get_active()
    items = []
    total_gain = Decimal("0")
    total_invested = Decimal("0")

    for asset in assets:
        returns = calc.calculate_total_return(asset.id)
        items.append(
            {
                "asset_id": returns.asset_id,
                "ticker": returns.ticker,
                "name": asset.name,
                "realized_gain": returns.realized_gain,
                "unrealized_gain": returns.unrealized_gain,
                "total_gain": returns.total_gain,
                "return_percentage": returns.return_percentage,
            }
        )
        total_gain += returns.total_gain
        holdings = calc.get_holdings(asset.id)
        total_invested += holdings.total_invested

    total_pct = (
        (total_gain / total_invested * 100) if total_invested > 0 else Decimal("0")
    )

    return {
        "items": items,
        "total_return": total_gain,
        "total_return_percentage": total_pct,
    }


@router.get("/history")
async def get_history(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    granularity: str = "daily",
    db: Session = Depends(get_db),
):
    """Histórico de evolución del patrimonio."""
    calc = CalculationService(db)
    portfolio = calc.calculate_portfolio_value()
    # Placeholder: en una implementación completa se reconstruiría el histórico
    # a partir de los precios históricos guardados.
    now = datetime.utcnow()
    return {
        "points": [
            {
                "date": now,
                "total_value": portfolio.current_value,
                "change": None,
                "change_percentage": None,
            }
        ],
        "max_value": portfolio.current_value,
        "min_value": portfolio.current_value,
        "avg_value": portfolio.current_value,
    }


@router.get("/wealth-evolution")
async def get_wealth_evolution(db: Session = Depends(get_db)):
    """Evolución histórica del patrimonio: efectivo, inversiones y total.

    Reconstruye el histórico combinando saldos de cuentas, operaciones
    y precios históricos de activos.
    """
    calc = CalculationService(db)
    points = calc.get_wealth_evolution()

    # Serializar Decimals a float para JSON
    serialized = [
        {
            "date": p["date"],
            "cash": float(p["cash"]),
            "investments": float(p["investments"]),
            "total": float(p["total"]),
            "by_type": {k: float(v) for k, v in p.get("by_type", {}).items()},
            "by_bank": {k: float(v) for k, v in p.get("by_bank", {}).items()},
        }
        for p in points
    ]
    return {"points": serialized}
