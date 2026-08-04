from uuid import UUID
from sqlalchemy.orm import Session
from features.profiles.schemas import (
    ProfileCreate,
    ProfileUpdate,
)
from features.profiles.models.profile import Profile
from features.profiles.models.food_allergy import FoodAllergy
from features.profiles.models.disliked_ingredient import DislikedIngredient
from sqlalchemy.orm import joinedload


def create_profile(
    db: Session,
    profile_data: ProfileCreate,
    auth_id: UUID
) -> Profile:

    profile = Profile(
        auth_id=auth_id,
        profile_image_url=profile_data.profile_image_url,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        date_of_birth=profile_data.date_of_birth,
        sex=profile_data.sex,
        daily_budget=profile_data.daily_budget,
        cooking_skill_level=profile_data.cooking_skill_level,
    )

    db.add(profile)
    db.flush()

    for allergy in profile_data.food_allergies:
        food_allergy = FoodAllergy(
            profile_id=profile.id,
            allergy=allergy,
        )
        db.add(food_allergy)

    for ingredient in profile_data.disliked_ingredients:
        disliked = DislikedIngredient(
            profile_id=profile.id,
            ingredient=ingredient,
        )
        db.add(disliked)

    db.commit()
    db.refresh(profile)

    return profile


def get_profile_by_auth_id(
    db: Session,
    auth_id: UUID
) -> Profile | None:

    return (
        db.query(Profile)
        .options(
            joinedload(Profile.food_allergies),
            joinedload(Profile.disliked_ingredients),
        )
        .filter(Profile.auth_id == auth_id)
        .first()
    )


def update_profile(
    db: Session,
    profile: Profile,
    profile_data: ProfileUpdate
) -> Profile:

    update_data = profile_data.model_dump(
        exclude_unset=True
    )

    food_allergies = update_data.pop(
        "food_allergies",
        None
    )

    disliked_ingredients = update_data.pop(
        "disliked_ingredients",
        None
    )

    # Update normal profile fields
    for key, value in update_data.items():
        setattr(profile, key, value)


    # Replace allergies
    if food_allergies is not None:
        db.query(FoodAllergy).filter(
            FoodAllergy.profile_id == profile.id
        ).delete(
            synchronize_session=False
        )

        for allergy in food_allergies:
            db.add(
                FoodAllergy(
                    profile_id=profile.id,
                    allergy=allergy
                )
            )


    # Replace disliked ingredients
    if disliked_ingredients is not None:
        db.query(DislikedIngredient).filter(
            DislikedIngredient.profile_id == profile.id
        ).delete(
            synchronize_session=False
        )

        for ingredient in disliked_ingredients:
            db.add(
                DislikedIngredient(
                    profile_id=profile.id,
                    ingredient=ingredient
                )
            )


    db.commit()

    return get_profile_by_auth_id(
        db,
        profile.auth_id
    )