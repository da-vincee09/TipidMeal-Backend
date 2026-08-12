from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class PantryItemCreate(BaseModel):
    ingredient: str = Field(
        min_length=1,
        max_length=100,
    )
    quantity: Decimal = Field(
        gt=0,
    )
    unit: str = Field(
        min_length=1,
        max_length=50,
    )


class PantryItemUpdate(BaseModel):
    ingredient: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    quantity: Decimal | None = Field(
        default=None,
        gt=0,
    )
    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )


class PantryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ingredient: str
    quantity: Decimal
    unit: str
    created_at: datetime
    updated_at: datetime