from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from core.dependencies import get_db
from shared.auth.dependencies import get_current_user

from features.favorites import service
from features.favorites.schemas import (
    FavoriteCreate,
    FavoriteResponse,
)

from features.profiles import service as profile_service


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)


@router.post(
    "",
    response_model=FavoriteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_favorite(
    favorite_data: FavoriteCreate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return service.create_favorite(
        db,
        profile.id,
        favorite_data.meal_id,
    )


@router.get(
    "",
    response_model=list[FavoriteResponse],
)
def get_favorites(
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return service.get_favorites_by_profile(
        db,
        profile.id,
    )


@router.delete(
    "/{meal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_favorite(
    meal_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    service.delete_favorite(
        db,
        profile.id,
        meal_id,
    )

    return None