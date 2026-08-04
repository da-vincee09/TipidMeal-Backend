from datetime import datetime
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

    age: int = Field(
        ge=13,
        le=120
    )

    sex: str

    daily_budget: float = Field(
        gt=0
    )

    cooking_skill_level: str

    food_allergies: str | None = None

    disliked_ingredients: str | None = None


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

    age: int | None = Field(
        default=None,
        ge=13,
        le=120
    )

    sex: str | None = None

    daily_budget: float | None = Field(
        default=None,
        gt=0
    )

    cooking_skill_level: str | None = None

    food_allergies: str | None = None

    disliked_ingredients: str | None = None


# Returned by API
class ProfileResponse(BaseModel):
    id: UUID
    auth_id: UUID

    profile_image_url: str | None = None

    first_name: str
    last_name: str

    age: int
    sex: str

    daily_budget: float

    cooking_skill_level: str

    food_allergies: str | None
    disliked_ingredients: str | None

    created_at: datetime
    updated_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )