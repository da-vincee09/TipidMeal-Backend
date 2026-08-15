from uuid import UUID
from sqlalchemy.orm import Session
from features.meals.models.meal import Meal
from features.meals.schemas import (
    MealCreate,
    MealUpdate,
)
from features.meals import repository
from decimal import Decimal
from fastapi import HTTPException, status


def create_meal(
    db: Session,
    meal_data: MealCreate,
) -> Meal:

    return repository.create_meal(
        db,
        meal_data,
    )

def create_meal_ingredient(
    db: Session,
    meal_id: UUID,
    ingredient: str,
    quantity: Decimal,
    unit: str,
    is_optional: bool,
):
    meal = repository.get_meal_by_id(
        db,
        meal_id,
    )

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    return repository.create_meal_ingredient(
        db,
        meal_id,
        ingredient,
        quantity,
        unit,
        is_optional,
    )


def create_meal_instruction(
    db: Session,
    meal_id: UUID,
    step_number: int,
    instruction: str,
):
    meal = repository.get_meal_by_id(
        db,
        meal_id,
    )

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    return repository.create_meal_instruction(
        db,
        meal_id,
        step_number,
        instruction,
    )


def get_meals(
    db: Session,
) -> list[Meal]:

    return repository.get_meals(
        db,
    )


def get_meal_by_id(
    db: Session,
    meal_id: UUID,
) -> Meal | None:

    return repository.get_meal_by_id(
        db,
        meal_id,
    )


def update_meal(
    db: Session,
    meal: Meal,
    meal_data: MealUpdate,
) -> Meal:

    return repository.update_meal(
        db,
        meal,
        meal_data,
    )


def delete_meal(
    db: Session,
    meal: Meal,
) -> None:

    repository.delete_meal(
        db,
        meal,
    )