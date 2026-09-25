"""Schemas de Pydantic para validación de la entidad Operation."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.enums import OperationType


class OperationBase(BaseModel):
    """Campos comunes de una operación."""

    asset_id: int
    account_id: int
    operation_type: OperationType
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0)
    commission: Decimal = Field(default=Decimal("0"), ge=0)
    operation_date: datetime
    notes: str | None = Field(default=None, max_length=1024)

    @model_validator(mode="after")
    def compute_total_amount(self) -> "OperationBase":
        self.total_amount = self.quantity * self.unit_price + self.commission
        return self

    @field_validator("operation_date")
    @classmethod
    def validate_date_not_future(cls, v: datetime) -> datetime:
        if v > datetime.utcnow():
            raise ValueError("operation_date cannot be in the future")
        return v


class OperationCreate(OperationBase):
    """Schema para crear una operación."""

    total_amount: Decimal | None = None


class OperationUpdate(BaseModel):
    """Schema para actualizar una operación."""

    quantity: Decimal | None = Field(default=None, gt=0)
    unit_price: Decimal | None = Field(default=None, gt=0)
    commission: Decimal | None = Field(default=None, ge=0)
    operation_date: datetime | None = None
    notes: str | None = None


class OperationRead(OperationBase):
    """Schema para retornar una operación."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime


class OperationReadFull(OperationRead):
    """Operación con datos de asset y account."""

    asset: "AssetRead" = {}  # noqa: F821
    account: "AccountRead" = {}  # noqa: F821

    model_config = ConfigDict(from_attributes=True)


class OperationBulkImport(BaseModel):
    """Resultado de una importación CSV de operaciones."""

    imported: int
    errors: list[str]


# Resolución de forward references
from app.schemas.account import AccountRead  # noqa: E402
from app.schemas.asset import AssetRead  # noqa: E402

OperationReadFull.model_rebuild()
