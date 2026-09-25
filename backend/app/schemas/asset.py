"""Schemas de Pydantic para validación de la entidad Asset."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import AssetType


class AssetBase(BaseModel):
    """Campos comunes de un activo."""

    ticker: str = Field(..., min_length=1, max_length=20)
    asset_type: AssetType
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    currency: str = Field(default="EUR", max_length=3)
    manual_price: bool = False

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not v.replace(".", "").replace("-", "").isalnum():
            raise ValueError(
                "Ticker must contain only alphanumeric characters, dots and hyphens"
            )
        return v.upper()

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if len(v) != 3 or not v.isalpha():
            raise ValueError("Currency must be a valid ISO 4217 code (3 letters)")
        return v.upper()


class AssetCreate(AssetBase):
    """Schema para crear un activo."""

    current_price: Decimal | None = Field(default=None, gt=0)


class AssetUpdate(BaseModel):
    """Schema para actualizar un activo."""

    ticker: str | None = Field(default=None, min_length=1, max_length=20)
    asset_type: AssetType | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    currency: str | None = None
    current_price: Decimal | None = Field(default=None, gt=0)
    manual_price: bool | None = None
    is_active: bool | None = None


class AssetRead(AssetBase):
    """Schema para retornar un activo."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    current_price: Decimal | None
    price_updated_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AssetReadWithOperations(AssetRead):
    """Activo con sus operaciones."""

    operations: list["OperationRead"] = []  # noqa: F821

    model_config = ConfigDict(from_attributes=True)


# Resolución de forward reference
from app.schemas.operation import OperationRead  # noqa: E402

AssetReadWithOperations.model_rebuild()
