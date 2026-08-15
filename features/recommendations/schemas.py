from pydantic import BaseModel, ConfigDict
from features.meals.schemas import MealResponse


class IngredientAdaptationResponse(BaseModel):
    ingredient: str
    action: str
    replacement: str | None


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


class RecommendationListResponse(BaseModel):
    recommendations: list[RecommendationResponse]