"""Schemas de Pydantic para validación de la entidad Price."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import PriceSource


class PriceBase(BaseModel):
    """Campos comunes de un precio."""

    asset_id: int
    price: Decimal = Field(..., gt=0)
    price_date: datetime
    source: PriceSource = PriceSource.MANUAL

    @field_validator("price_date")
    @classmethod
    def validate_date_not_future(cls, v: datetime) -> datetime:
        if v > datetime.utcnow():
            raise ValueError("price_date cannot be in the future")
        return v


class PriceCreate(PriceBase):
    """Schema para crear un precio manualmente."""


class PriceRead(PriceBase):
    """Schema para retornar un precio."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class PriceCurrent(BaseModel):
    """Respuesta del precio actual con metadata."""

    price: Decimal
    source: str
    timestamp: datetime
