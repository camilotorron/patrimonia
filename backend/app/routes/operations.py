"""Rutas API para gestionar operaciones."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import OperationType
from app.schemas.operation import OperationCreate, OperationRead, OperationUpdate
from app.services.csv_importer import CSVImporter
from app.services.operation_service import OperationService

router = APIRouter()


@router.get("", response_model=list[OperationRead])
@router.get("/", response_model=list[OperationRead], include_in_schema=False)
async def list_operations(
    skip: int = 0,
    limit: int = 100,
    asset_id: int | None = None,
    account_id: int | None = None,
    operation_type: OperationType | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    db: Session = Depends(get_db),
):
    """Lista operaciones con filtros opcionales."""
    service = OperationService(db)

    if asset_id is not None:
        ops = service.operation_repo.get_by_asset(asset_id)
    elif account_id is not None:
        ops = service.operation_repo.get_by_account(account_id)
    elif start_date is not None and end_date is not None:
        ops = service.operation_repo.get_by_date_range(start_date, end_date)
    else:
        ops = service.operation_repo.get_all(skip=skip, limit=limit)

    if operation_type is not None:
        ops = [o for o in ops if o.operation_type == operation_type]

    return ops[skip : skip + limit]


@router.get("/{op_id}", response_model=OperationRead)
async def get_operation(op_id: int, db: Session = Depends(get_db)):
    """Obtiene una operación por su ID."""
    service = OperationService(db)
    op = service.operation_repo.get(op_id)
    if op is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found"
        )
    return op


@router.post("", response_model=OperationRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=OperationRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_operation(data: OperationCreate, db: Session = Depends(get_db)):
    """Crea una operación de compra o venta."""
    service = OperationService(db)
    try:
        if data.operation_type == OperationType.BUY:
            op = service.create_buy_operation(
                asset_id=data.asset_id,
                account_id=data.account_id,
                quantity=data.quantity,
                unit_price=data.unit_price,
                commission=data.commission,
                operation_date=data.operation_date,
                notes=data.notes,
            )
        else:
            op = service.create_sell_operation(
                asset_id=data.asset_id,
                account_id=data.account_id,
                quantity=data.quantity,
                unit_price=data.unit_price,
                commission=data.commission,
                operation_date=data.operation_date,
                notes=data.notes,
            )
        db.commit()
        db.refresh(op)
        return op
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.put("/{op_id}", response_model=OperationRead)
async def update_operation(
    op_id: int, data: OperationUpdate, db: Session = Depends(get_db)
):
    """Actualiza una operación (solo si tiene menos de 7 días)."""
    service = OperationService(db)
    try:
        op = service.update_operation(op_id, data.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    if op is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found"
        )
    db.commit()
    db.refresh(op)
    return op


@router.delete("/{op_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operation(op_id: int, db: Session = Depends(get_db)):
    """Revierte y elimina una operación."""
    service = OperationService(db)
    if not service.cancel_operation(op_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found"
        )
    db.commit()


@router.post("/import")
async def import_operations_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Importa operaciones desde un archivo CSV."""
    content = (await file.read()).decode("utf-8")

    # Construir mapas de nombres → IDs
    from app.repositories.account_repository import AccountRepository
    from app.repositories.asset_repository import AssetRepository

    accounts = {a.name: a.id for a in AccountRepository(db).get_all(limit=10000)}
    assets = {a.ticker: a.id for a in AssetRepository(db).get_all(limit=10000)}

    importer = CSVImporter(db)
    try:
        result = importer.import_operations(content, accounts, assets)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    return result
