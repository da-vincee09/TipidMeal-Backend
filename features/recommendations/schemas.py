from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from features.meals.schemas import MealResponse
from features.nutrition.schemas import NutritionAdequacyResponse


class IngredientAdaptationResponse(BaseModel):
    ingredient: str
    action: str
    replacement: str | None
    available_quantity: Decimal | None = None
    required_quantity: Decimal | None = None
    unit: str | None = None


class MealAdaptationResponse(BaseModel):
    decision: str
    ingredients: list[IngredientAdaptationResponse]


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    meal: MealResponse

    coverage: float

    budget_score: float
    skill_score: float
    allergy_score: float
    disliked_score: float

    hybrid_score: float

    adaptation: MealAdaptationResponse

    nutrition: NutritionAdequacyResponse


class RecommendationListResponse(BaseModel):
    recommendations: list[RecommendationResponse]