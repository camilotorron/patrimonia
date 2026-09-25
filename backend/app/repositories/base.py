"""Repositorio genérico base para acceso a datos."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Repository genérico con operaciones CRUD estándar.

    Las subclases deben definir :attr:`model` con el modelo SQLAlchemy
    correspondiente.
    """

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------ #
    # Read
    # ------------------------------------------------------------------ #
    def get(self, obj_id: int) -> ModelT | None:
        return self.db.get(self.model, obj_id)

    def get_all(self, skip: int = 0, limit: int = 50) -> list[ModelT]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def filter_by(self, **kwargs: Any) -> list[ModelT]:
        stmt = select(self.model).filter_by(**kwargs)
        return list(self.db.execute(stmt).scalars().all())

    def count(self) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        return self.db.execute(stmt).scalar() or 0

    # ------------------------------------------------------------------ #
    # Write
    # ------------------------------------------------------------------ #
    def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def update(self, obj_id: int, data: dict[str, Any]) -> ModelT | None:
        obj = self.get(obj_id)
        if obj is None:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(obj, key, value)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def delete(self, obj_id: int) -> bool:
        obj = self.get(obj_id)
        if obj is None:
            return False
        self.db.delete(obj)
        self.db.flush()
        return True

    # ------------------------------------------------------------------ #
    # Bulk
    # ------------------------------------------------------------------ #
    def bulk_create(self, objs: list[ModelT]) -> list[ModelT]:
        self.db.add_all(objs)
        self.db.flush()
        return objs
