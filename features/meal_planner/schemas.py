from uuid import UUID
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MealPlanMealSummary(BaseModel):
    id: UUID
    name: str
    estimated_cost: Decimal
    image_url: str | None
    
    model_config = ConfigDict(
        from_attributes=True,
    )


class MealPlanEntryCreate(BaseModel):
    meal_id: UUID
    planned_date: date

    meal_slot: str | None = Field(
        default=None,
        max_length=50,
    )


class MealPlanEntryUpdate(BaseModel):
    planned_date: date | None = None

    meal_slot: str | None = Field(
        default=None,
        max_length=50,
    )


class MealPlanEntryResponse(BaseModel):
    id: UUID
    meal: MealPlanMealSummary
    planned_date: date
    meal_slot: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class WeeklyPlanResponse(BaseModel):
    start_date: date
    end_date: date
    entries: list[MealPlanEntryResponse]
    estimated_cost_total: Decimal