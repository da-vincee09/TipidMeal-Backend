from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

# Used when creating a profile
class ProfileCreate(BaseModel):
    profile_image_url: str | None = None

    first_name: str = Field(
        min_length=2,
        max_length=100
    )

    last_name: str = Field(
        min_length=2,
        max_length=100
    )

    date_of_birth: date

    sex: str

    daily_budget: float = Field(
        gt=0
    )

    cooking_skill_level: str

    food_allergies: list[str] = Field(default_factory=list)
    disliked_ingredients: list[str] = Field(default_factory=list)


# Used when updating a profile
class ProfileUpdate(BaseModel):
    profile_image_url: str | None = None

    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    date_of_birth: date | None = None

    sex: str | None = None

    daily_budget: float | None = Field(
        default=None,
        gt=0
    )

    cooking_skill_level: str | None = None

    food_allergies: list[str] | None = None
    disliked_ingredients: list[str] | None = None


class FoodAllergyResponse(BaseModel):
    id: UUID
    allergy: str

    model_config = ConfigDict(
        from_attributes=True
    )


class DislikedIngredientResponse(BaseModel):
    id: UUID
    ingredient: str

    model_config = ConfigDict(
        from_attributes=True
    )

# Returned by API
class ProfileResponse(BaseModel):
    id: UUID
    auth_id: UUID

    profile_image_url: str | None = None

    first_name: str
    last_name: str

    date_of_birth: date
    sex: str

    daily_budget: float

    cooking_skill_level: str

    food_allergies: list[FoodAllergyResponse]
    disliked_ingredients: list[DislikedIngredientResponse]

    created_at: datetime
    updated_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )

