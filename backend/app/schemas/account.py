"""Schemas de Pydantic para validación de la entidad Account."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import AccountType


class AccountBase(BaseModel):
    """Campos comunes de una cuenta."""

    name: str = Field(..., min_length=1, max_length=255)
    account_type: AccountType
    bank: str = Field(..., min_length=1, max_length=255)
    iban: str | None = Field(default=None, max_length=64)
    currency: str = Field(default="EUR", max_length=3)
    current_balance: Decimal = Field(default=Decimal("0"), ge=0)

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Currency must be a valid ISO 4217 code (3 letters)")
        return v.upper()


class AccountCreate(AccountBase):
    """Schema para crear una cuenta."""


class AccountUpdate(BaseModel):
    """Schema para actualizar una cuenta (campos opcionales)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    account_type: AccountType | None = None
    bank: str | None = Field(default=None, min_length=1, max_length=255)
    iban: str | None = None
    currency: str | None = Field(default=None, max_length=3)
    current_balance: Decimal | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Currency must be a valid ISO 4217 code (3 letters)")
        return v.upper()


class AccountRead(AccountBase):
    """Schema para retornar una cuenta en respuestas."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AccountReadWithOperations(AccountRead):
    """Cuenta con sus operaciones."""

    operations: list["OperationRead"] = []  # noqa: F821 – forward ref

    model_config = ConfigDict(from_attributes=True)


# Resolución de forward reference
from app.schemas.operation import OperationRead  # noqa: E402

AccountReadWithOperations.model_rebuild()
