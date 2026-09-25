"""Rutas API para gestionar activos."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.account import Account
from app.models.enums import AssetType
from app.schemas.asset import AssetCreate, AssetRead, AssetUpdate
from app.services.asset_service import AssetService
from app.services.calculation_service import CalculationService

router = APIRouter()


@router.get("", response_model=list[AssetRead])
@router.get("/", response_model=list[AssetRead], include_in_schema=False)
async def list_assets(
    skip: int = 0,
    limit: int = 50,
    asset_type: AssetType | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db),
):
    """Lista todos los activos (con filtros opcionales)."""
    service = AssetService(db)
    if asset_type is not None:
        assets = service.repo.get_by_type(asset_type)
    else:
        assets = service.repo.get_all(skip=skip, limit=limit)
    if active is not None:
        assets = [a for a in assets if a.is_active == active]
    return assets


@router.get("/search")
async def search_assets(
    query: str = Query(..., min_length=1), db: Session = Depends(get_db)
):
    """Busca activos por ticker o nombre."""
    service = AssetService(db)
    return service.search_assets(query)


@router.get("/ticker/{ticker}", response_model=AssetRead)
async def get_asset_by_ticker(ticker: str, db: Session = Depends(get_db)):
    """Busca un activo por su ticker."""
    service = AssetService(db)
    asset = service.repo.get_by_ticker(ticker)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )
    return asset


@router.get("/{asset_id}", response_model=AssetRead)
async def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Obtiene un activo por su ID."""
    service = AssetService(db)
    asset = service.repo.get(asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )
    return asset


@router.post("", response_model=AssetRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=AssetRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_asset(data: AssetCreate, db: Session = Depends(get_db)):
    """Crea un nuevo activo."""
    service = AssetService(db)
    try:
        asset = service.create_asset(data.model_dump())
        db.commit()
        db.refresh(asset)
        return asset
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.put("/{asset_id}", response_model=AssetRead)
async def update_asset(asset_id: int, data: AssetUpdate, db: Session = Depends(get_db)):
    """Actualiza un activo existente."""
    service = AssetService(db)
    asset = service.update_asset(asset_id, data.model_dump(exclude_unset=True))
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )
    db.commit()
    db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """Desactiva un activo (soft delete)."""
    service = AssetService(db)
    asset = service.deprecate_asset(asset_id)
    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )
    db.commit()


@router.get("/{asset_id}/holdings")
async def get_asset_holdings(asset_id: int, db: Session = Depends(get_db)):
    """Posición actual de un activo: cantidad, precio medio, valor, ganancia."""
    calc = CalculationService(db)
    try:
        h = calc.get_holdings(asset_id)
        return {
            "quantity": h.quantity,
            "average_price": h.average_price,
            "total_invested": h.total_invested,
            "current_value": h.current_value,
            "gain": h.gain,
            "gain_percentage": h.gain_percentage,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.get("/overview/snapshot")
async def get_assets_snapshot(db: Session = Depends(get_db)):
    """Lista todos los activos con banco, cantidad, valor total y rentabilidad."""
    from app.models.operation import Operation
    from sqlalchemy import select

    calc = CalculationService(db)
    assets = calc.asset_repo.get_active()

    results = []
    for asset in assets:
        h = calc.get_holdings(asset.id)

        # Obtener el banco de la cuenta donde está el activo
        stmt = (
            select(Account.name, Account.bank)
            .join(Operation, Operation.account_id == Account.id)
            .where(Operation.asset_id == asset.id)
            .distinct()
        )
        account_rows = db.execute(stmt).all()
        banks = [f"{r.bank}" for r in account_rows] if account_rows else []

        results.append(
            {
                "id": asset.id,
                "ticker": asset.ticker,
                "name": asset.name,
                "asset_type": asset.asset_type.value,
                "currency": asset.currency,
                "current_price": asset.current_price,
                "banks": banks,
                "quantity": h.quantity,
                "current_value": h.current_value,
                "total_invested": h.total_invested,
                "gain": h.gain,
                "gain_percentage": h.gain_percentage,
            }
        )
    return results
