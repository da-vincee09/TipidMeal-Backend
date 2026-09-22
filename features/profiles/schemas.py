from datetime import datetime, date
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator
from features.profiles.models.profile import CookingSkillLevel, PhysicalActivityLevel

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

    budget_per_meal: float = Field(
        gt=0
    )

    cooking_skill_level: CookingSkillLevel

    @field_validator("cooking_skill_level", mode="before")
    @classmethod
    def normalize_skill_level(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

    physical_activity_level: PhysicalActivityLevel

    @field_validator("physical_activity_level", mode="before")
    @classmethod
    def normalize_activity_level(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

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

    budget_per_meal: float | None = Field(
        default=None,
        gt=0
    )

    cooking_skill_level: CookingSkillLevel | None = None

    @field_validator("cooking_skill_level", mode="before")
    @classmethod
    def normalize_skill_level(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

    physical_activity_level: PhysicalActivityLevel | None = None

    @field_validator("physical_activity_level", mode="before")
    @classmethod
    def normalize_activity_level(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

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

    budget_per_meal: float

    cooking_skill_level: CookingSkillLevel

    physical_activity_level: PhysicalActivityLevel | None = None

    food_allergies: list[FoodAllergyResponse]
    disliked_ingredients: list[DislikedIngredientResponse]

    created_at: datetime
    updated_at: datetime


    model_config = ConfigDict(
        from_attributes=True
    )

