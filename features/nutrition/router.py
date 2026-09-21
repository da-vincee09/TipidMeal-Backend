from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_db
from shared.auth.dependencies import get_current_user

from features.meals import service as meals_service
from features.profiles.service import get_profile_by_auth_id
from features.nutrition.schemas import NutritionAdequacyResponse
from features.nutrition.service import compute_nutritional_adequacy


router = APIRouter(
    prefix="/meals",
    tags=["Nutrition"],
)


@router.get(
    "/{meal_id}/nutrition-adequacy",
    response_model=NutritionAdequacyResponse,
)
def get_meal_nutrition_adequacy(
    meal_id: UUID,
    auth_id=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print("=== NUTRITION DEBUG ===")
    print("auth_id:", auth_id)
    print("meal_id:", meal_id)

    meal = meals_service.get_meal_by_id(db, meal_id)
    print("meal:", meal)

    if meal is None:
        print(">>> MEAL IS NONE")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    profile = get_profile_by_auth_id(db, auth_id)
    print("profile:", profile)

    if profile is None:
        print(">>> PROFILE IS NONE")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    print(">>> BOTH FOUND")
    print(">>> COMPUTING NUTRITION")

    result = compute_nutritional_adequacy(db, meal, profile)

    print(">>> RESULT:", result)

    return result