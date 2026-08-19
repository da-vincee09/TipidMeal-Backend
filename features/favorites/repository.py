from uuid import UUID
from sqlalchemy.orm import Session

from features.favorites.models.favorite import Favorite


def create_favorite(
    db: Session,
    profile_id: UUID,
    meal_id: UUID,
) -> Favorite:

    favorite = Favorite(
        profile_id=profile_id,
        meal_id=meal_id,
    )

    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return favorite


def get_favorite_by_profile_and_meal(
    db: Session,
    profile_id: UUID,
    meal_id: UUID,
) -> Favorite | None:

    return (
        db.query(Favorite)
        .filter(
            Favorite.profile_id == profile_id,
            Favorite.meal_id == meal_id,
        )
        .first()
    )


def get_favorites_by_profile(
    db: Session,
    profile_id: UUID,
) -> list[Favorite]:

    return (
        db.query(Favorite)
        .filter(Favorite.profile_id == profile_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


def delete_favorite(
    db: Session,
    favorite: Favorite,
) -> None:

    db.delete(favorite)
    db.commit()