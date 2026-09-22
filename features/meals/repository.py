from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from features.meals.models.meal import Meal
from features.meals.schemas import (
    MealCreate,
    MealUpdate,
)
from features.meals.models.meal_ingredient import MealIngredient
from features.meals.models.meal_instruction import MealInstruction
from features.ingredients.repository import get_or_create_ingredient
from features.ingredients.models.ingredient import Ingredient
from decimal import Decimal
from sqlalchemy import select


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
    ingredient_row = get_or_create_ingredient(db, ingredient)

    meal_ingredient = MealIngredient(
        meal_id=meal_id,
        ingredient_id=ingredient_row.id,
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
            joinedload(Meal.ingredients).joinedload(MealIngredient.ingredient_ref),
            joinedload(Meal.instructions),
        )
        .all()
    )


def get_ingredient_suggestions(
    db: Session,
    search: str,
    limit: int = 10,
) -> list[dict]:
    # Rewritten to join through Ingredient, since ingredient names now
    # live there, not as a column on MealIngredient.
    stmt = (
        select(Ingredient.name, MealIngredient.unit)
        .join(MealIngredient, MealIngredient.ingredient_id == Ingredient.id)
        .where(Ingredient.name.ilike(f"%{search}%"))
        .distinct()
        .order_by(Ingredient.name)
    )
    rows = db.execute(stmt).all()

    grouped: dict[str, list[str]] = {}
    for ingredient, unit in rows:
        if ingredient not in grouped and len(grouped) >= limit:
            continue
        units = grouped.setdefault(ingredient, [])
        if unit not in units:
            units.append(unit)

    return [
        {"ingredient": ingredient, "units": units}
        for ingredient, units in grouped.items()
    ]


def get_all_units(db: Session) -> list[str]:
    stmt = (
        select(MealIngredient.unit)
        .distinct()
        .order_by(MealIngredient.unit)
    )
    return list(db.execute(stmt).scalars().all())


def get_meal_by_id(
    db: Session,
    meal_id: UUID,
) -> Meal | None:

    return (
        db.query(Meal)
        .options(
            joinedload(Meal.ingredients).joinedload(MealIngredient.ingredient_ref),
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