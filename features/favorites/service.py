from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from features.favorites import repository
from features.favorites.models.favorite import Favorite
from features.meals import service as meal_service


def create_favorite(
    db: Session,
    profile_id: UUID,
    meal_id: UUID,
) -> Favorite:

    meal = meal_service.get_meal_by_id(
        db,
        meal_id,
    )

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    existing = repository.get_favorite_by_profile_and_meal(
        db,
        profile_id,
        meal_id,
    )

    # Idempotent: favoriting an already-favorited meal just returns
    # the existing row instead of raising a conflict error, so the
    # Flutter optimistic-UI toggle never has to special-case this.
    if existing is not None:
        return existing

    return repository.create_favorite(
        db,
        profile_id,
        meal_id,
    )


def get_favorites_by_profile(
    db: Session,
    profile_id: UUID,
) -> list[Favorite]:

    return repository.get_favorites_by_profile(
        db,
        profile_id,
    )


def delete_favorite(
    db: Session,
    profile_id: UUID,
    meal_id: UUID,
) -> None:

    favorite = repository.get_favorite_by_profile_and_meal(
        db,
        profile_id,
        meal_id,
    )

    # Idempotent on delete too: un-favoriting something that isn't
    # favorited (e.g. a double-tap race) is a no-op, not a 404.
    if favorite is None:
        return

    repository.delete_favorite(
        db,
        favorite,
    )