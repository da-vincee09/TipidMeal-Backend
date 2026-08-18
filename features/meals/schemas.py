from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class MealIngredientCreate(BaseModel):
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

    is_optional: bool = False


class MealInstructionCreate(BaseModel):
    step_number: int = Field(
        gt=0,
    )

    instruction: str = Field(
        min_length=1,
        max_length=500,
    )

    
class MealIngredientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ingredient: str
    quantity: Decimal
    unit: str
    is_optional: bool


class MealInstructionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    step_number: int
    instruction: str


class MealCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    image_url: str | None = None

    estimated_cost: Decimal = Field(
        gt=0,
    )

    cooking_time: int = Field(
        gt=0,
    )

    difficulty: str = Field(
        min_length=1,
        max_length=50,
    )

    servings: int = Field(
        gt=0,
    )

    calories: int | None = Field(
        default=None,
        gt=0,
    )


class MealUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = None

    image_url: str | None = None

    estimated_cost: Decimal | None = Field(
        default=None,
        gt=0,
    )

    cooking_time: int | None = Field(
        default=None,
        gt=0,
    )

    difficulty: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    servings: int | None = Field(
        default=None,
        gt=0,
    )

    calories: int | None = Field(
        default=None,
        gt=0,
    )


class MealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    image_url: str | None
    estimated_cost: Decimal
    cooking_time: int
    difficulty: str
    servings: int
    calories: int | None
    created_at: datetime
    updated_at: datetime

    ingredients: list[MealIngredientResponse]
    instructions: list[MealInstructionResponse]


class MealListResponse(BaseModel):
    meals: list[MealResponse]


class IngredientSuggestionResponse(BaseModel):
    ingredient: str
    units: list[str]