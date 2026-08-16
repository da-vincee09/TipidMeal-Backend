from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from features.meals.models.meal import Meal
from features.meals.schemas import (
    MealCreate,
    MealUpdate,
)
from features.meals.models.meal_ingredient import MealIngredient
from features.meals.models.meal_instruction import MealInstruction
from decimal import Decimal
from sqlalchemy import select
from features.meals.models.meal_ingredient import MealIngredient


def create_meal(
    db: Session,
    meal_data: MealCreate,
) -> Meal:

    meal = Meal(
        name=meal_data.name,
        description=meal_data.description,
        image_url=meal_data.image_url,
        estimated_cost=meal_data.estimated_cost,
        cooking_time=meal_data.cooking_time,
        difficulty=meal_data.difficulty,
        servings=meal_data.servings,
        calories=meal_data.calories,
    )

    db.add(meal)
    db.commit()
    db.refresh(meal)

    return meal


def create_meal_ingredient(
    db: Session,
    meal_id: UUID,
    ingredient: str,
    quantity: Decimal,
    unit: str,
    is_optional: bool,
) -> MealIngredient:
    meal_ingredient = MealIngredient(
        meal_id=meal_id,
        ingredient=ingredient,
        quantity=quantity,
        unit=unit,
        is_optional=is_optional,
    )

    db.add(meal_ingredient)
    db.commit()
    db.refresh(meal_ingredient)

    return meal_ingredient


def create_meal_instruction(
    db: Session,
    meal_id: UUID,
    step_number: int,
    instruction: str,
) -> MealInstruction:
    meal_instruction = MealInstruction(
        meal_id=meal_id,
        step_number=step_number,
        instruction=instruction,
    )

    db.add(meal_instruction)
    db.commit()
    db.refresh(meal_instruction)

    return meal_instruction

def get_meals(
    db: Session,
) -> list[Meal]:

    return (
        db.query(Meal)
        .options(
            joinedload(Meal.ingredients),
            joinedload(Meal.instructions),
        )
        .all()
    )


def get_ingredient_suggestions(
    db: Session,
    search: str,
    limit: int = 10,
) -> list[str]:
    stmt = (
        select(MealIngredient.ingredient)
        .where(MealIngredient.ingredient.ilike(f"%{search}%"))
        .distinct()
        .order_by(MealIngredient.ingredient)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def get_meal_by_id(
    db: Session,
    meal_id: UUID,
) -> Meal | None:

    return (
        db.query(Meal)
        .options(
            joinedload(Meal.ingredients),
            joinedload(Meal.instructions),
        )
        .filter(
            Meal.id == meal_id,
        )
        .first()
    )


def update_meal(
    db: Session,
    meal: Meal,
    meal_data: MealUpdate,
) -> Meal:

    update_data = meal_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(meal, key, value)

    db.commit()
    db.refresh(meal)

    return meal


def delete_meal(
    db: Session,
    meal: Meal,
) -> None:

    db.delete(meal)
    db.commit()