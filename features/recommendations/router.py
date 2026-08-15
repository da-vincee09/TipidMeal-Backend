from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.dependencies import get_db
from shared.auth.dependencies import get_current_user

from features.profiles.service import get_profile_by_auth_id
from features.recommendations import service
from features.recommendations.schemas import RecommendationListResponse


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


@router.get(
    "",
    response_model=RecommendationListResponse,
)
def get_recommendations(
    auth_id = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = get_profile_by_auth_id(
        db,
        auth_id,
    )

    if profile is None:
        return {
            "recommendations": [],
        }

    recommendations = service.calculate_meal_coverage(
        db,
        profile.id,
    )

    return {
        "recommendations": recommendations,
    }