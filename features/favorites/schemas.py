from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FavoriteMealSummary(BaseModel):
    id: UUID
    name: str
    estimated_cost: Decimal
    image_url: str | None

    model_config = ConfigDict(
        from_attributes=True,
    )


class FavoriteCreate(BaseModel):
    meal_id: UUID


class FavoriteResponse(BaseModel):
    id: UUID
    meal: FavoriteMealSummary
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )