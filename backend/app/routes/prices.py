"""Rutas API para gestión de precios."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price import PriceCreate, PriceRead
from app.services.price_provider import YFinancePriceProvider
from app.services.price_service import PriceService

router = APIRouter()


@router.get("/asset/{asset_id}", response_model=list[PriceRead])
async def get_price_history(
    asset_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Histórico de precios de un activo."""
    service = PriceService(db)
    prices = service.price_repo.get_history(asset_id)
    return prices[skip : skip + limit]


@router.get("/asset/{asset_id}/latest", response_model=PriceRead | None)
async def get_latest_price(asset_id: int, db: Session = Depends(get_db)):
    """Último precio registrado de un activo."""
    service = PriceService(db)
    return service.price_repo.get_latest(asset_id)


@router.get("/asset/{asset_id}/current")
async def get_current_price(asset_id: int, db: Session = Depends(get_db)):
    """Precio actual: intenta caché / yfinance / último conocido."""
    service = PriceService(db)
    price = service.get_current_price(asset_id)
    if price is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No price available for this asset",
        )
    return {"price": price, "asset_id": asset_id}


@router.post("", response_model=PriceRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=PriceRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_manual_price(data: PriceCreate, db: Session = Depends(get_db)):
    """Crea un precio manual para un activo."""
    from app.models.price import Price

    price = Price(
        asset_id=data.asset_id,
        price=data.price,
        price_date=data.price_date,
        source=data.source,
    )
    service = PriceService(db)
    service.price_repo.create(price)
    db.commit()
    db.refresh(price)
    return price


@router.post("/refresh/{asset_id}")
async def refresh_price(asset_id: int, db: Session = Depends(get_db)):
    """Fuerza la actualización del precio de un activo desde yfinance."""
    service = PriceService(db)
    result = service.refresh_asset_price(asset_id)
    return {
        "old_price": result.old_price,
        "new_price": result.new_price,
        "timestamp": result.timestamp,
        "success": result.success,
        "error": result.error,
    }


@router.post("/refresh-all")
async def refresh_all_prices(db: Session = Depends(get_db)):
    """Actualiza los precios de todos los activos activos."""
    service = PriceService(db)
    result = service.refresh_all_prices()
    return {
        "updated_count": result.updated_count,
        "failed_count": result.failed_count,
        "details": [
            {
                "asset_id": r.asset_id,
                "ticker": r.ticker,
                "new_price": r.new_price,
                "success": r.success,
                "error": r.error,
            }
            for r in result.updated + result.failed
        ],
    }


@router.get("/search")
async def search_ticker(query: str, db: Session = Depends(get_db)):
    """Busca tickers en yfinance (para autocomplete)."""
    provider = YFinancePriceProvider()
    return provider.search_ticker(query)
