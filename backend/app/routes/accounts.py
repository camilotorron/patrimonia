"""Rutas API para gestionar cuentas."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.account import AccountCreate, AccountRead, AccountUpdate
from app.services.account_service import AccountService

router = APIRouter()


@router.get("/balance-evolution")
async def get_balance_evolution(db: Session = Depends(get_db)):
    """Retorna la evolución de saldos de todas las cuentas para graficar.

    Estructura:
      {
        "accounts": [{ "id", "name", "bank", "color" }, ...],
        "points": [ { "date", "balances": { "1": 1000, "2": 2000, "total": 3000 } }, ... ]
      }

    El primer punto es siempre el 2024-01-01 con los saldos iniciales.
    """
    from datetime import datetime
    from decimal import Decimal

    from app.models.account_balance import AccountBalance
    from sqlalchemy import select

    service = AccountService(db)
    accounts = service.repo.get_all(limit=10000)

    if not accounts:
        return {"accounts": [], "points": []}

    # Colores asignados a cada cuenta
    COLORS = [
        "#6366f1",
        "#10b981",
        "#f59e0b",
        "#ef4444",
        "#8b5cf6",
        "#06b6d4",
        "#ec4899",
        "#84cc16",
    ]

    account_info = [
        {
            "id": a.id,
            "name": a.name,
            "bank": a.bank,
            "color": COLORS[i % len(COLORS)],
        }
        for i, a in enumerate(accounts)
    ]
    account_ids = [a.id for a in accounts]

    # Recopilar todos los registros de saldo histórico
    stmt = (
        select(AccountBalance)
        .where(AccountBalance.account_id.in_(account_ids))
        .order_by(AccountBalance.recorded_at)
    )
    records = db.execute(stmt).scalars().all()

    # Punto inicial: 2024-01-01 con current_balance de cada cuenta
    start_date = datetime(2024, 1, 1)
    initial_balances = {}
    for acc in accounts:
        initial_balances[str(acc.id)] = float(acc.current_balance)

    # Si ya hay un registro en esa fecha exacta, usarlo
    points = []
    initial_point = {
        "date": start_date.isoformat(),
        "balances": dict(initial_balances),
    }
    initial_point["balances"]["total"] = sum(initial_balances.values())
    points.append(initial_point)

    # Puntos posteriores: para cada registro, llevar adelante el último saldo conocido de cada cuenta
    # y añadir el nuevo saldo de la cuenta que se actualizó
    current_balances = dict(initial_balances)

    for record in records:
        current_balances[str(record.account_id)] = float(record.balance)
        balances_copy = dict(current_balances)
        balances_copy["total"] = sum(balances_copy.values())
        points.append(
            {
                "date": record.recorded_at.isoformat(),
                "balances": balances_copy,
            }
        )

    return {"accounts": account_info, "points": points}


@router.get("", response_model=list[AccountRead])
@router.get("/", response_model=list[AccountRead], include_in_schema=False)
async def list_accounts(
    skip: int = 0,
    limit: int = 50,
    active: bool | None = None,
    db: Session = Depends(get_db),
):
    """Lista todas las cuentas (con paginación y filtro por activo)."""
    service = AccountService(db)
    accounts = service.repo.get_all(skip=skip, limit=limit)
    if active is not None:
        accounts = [a for a in accounts if a.is_active == active]
    return accounts


@router.get("/{account_id}", response_model=AccountRead)
async def get_account(account_id: int, db: Session = Depends(get_db)):
    """Obtiene una cuenta por su ID."""
    service = AccountService(db)
    account = service.repo.get(account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    return account


@router.post("", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=AccountRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    """Crea una nueva cuenta."""
    service = AccountService(db)
    try:
        account = service.create_account(data.model_dump())
        db.commit()
        db.refresh(account)
        return account
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.put("/{account_id}", response_model=AccountRead)
async def update_account(
    account_id: int, data: AccountUpdate, db: Session = Depends(get_db)
):
    """Actualiza una cuenta existente."""
    service = AccountService(db)
    account = service.update_account(account_id, data.model_dump(exclude_unset=True))
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Elimina o desactiva una cuenta."""
    service = AccountService(db)
    if not service.delete_account(account_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    db.commit()


@router.get("/{account_id}/balance")
async def get_account_balance(account_id: int, db: Session = Depends(get_db)):
    """Retorna el saldo actual de una cuenta."""
    service = AccountService(db)
    account = service.repo.get(account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )
    return {"balance": account.current_balance, "as_of": account.updated_at}


@router.post("/{account_id}/balance")
async def update_account_balance(
    account_id: int,
    data: dict,
    db: Session = Depends(get_db),
):
    """Actualiza el saldo de una cuenta y guarda el registro con timestamp."""
    from datetime import datetime
    from decimal import Decimal

    from app.models.account_balance import AccountBalance

    service = AccountService(db)
    account = service.repo.get(account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    balance = data.get("balance")
    if balance is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="balance is required",
        )

    balance = Decimal(str(balance))
    now = datetime.utcnow()

    # Guardar el registro histórico
    record = AccountBalance(
        account_id=account_id,
        balance=balance,
        recorded_at=now,
    )
    db.add(record)

    # Actualizar el saldo actual de la cuenta
    account.current_balance = balance
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "account_id": account_id,
        "balance": balance,
        "recorded_at": now,
    }


@router.get("/{account_id}/balance/history")
async def get_balance_history(account_id: int, db: Session = Depends(get_db)):
    """Retorna el histórico de saldos de una cuenta."""
    from app.models.account_balance import AccountBalance
    from sqlalchemy import select

    service = AccountService(db)
    account = service.repo.get(account_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    stmt = (
        select(AccountBalance)
        .where(AccountBalance.account_id == account_id)
        .order_by(AccountBalance.recorded_at)
    )
    records = db.execute(stmt).scalars().all()
    return [
        {
            "balance": r.balance,
            "recorded_at": r.recorded_at,
        }
        for r in records
    ]


@router.get("/{account_id}/summary")
async def get_account_summary(account_id: int, db: Session = Depends(get_db)):
    """Resumen financiero de una cuenta: saldo, valor de activos y total."""
    service = AccountService(db)
    try:
        summary = service.get_account_summary(account_id)
        return {
            "balance": summary.balance,
            "assets_value": summary.assets_value,
            "total": summary.total,
            "currencies": summary.currencies,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
