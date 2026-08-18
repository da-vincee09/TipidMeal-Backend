from decimal import Decimal
from uuid import UUID
from datetime import date

from sqlalchemy.orm import Session

from features.grocery_list.schemas import (
    GroceryListItem,
    GroceryListResponse,
)

from features.meal_planner import (
    repository as meal_plan_repository,
)

from features.pantry import (
    repository as pantry_repository,
)

from features.recommendations.utils import (
    normalize_ingredient,
)


def aggregate_required_ingredients(
    meal_plan_entries,
) -> dict[tuple[str, str], Decimal]:

    required: dict[
        tuple[str, str],
        Decimal,
    ] = {}

    for entry in meal_plan_entries:
        meal = entry.meal

        for ingredient in meal.ingredients:
            ingredient_name = normalize_ingredient(
                ingredient.ingredient
            )

            unit = ingredient.unit.strip().lower()

            key = (
                ingredient_name,
                unit,
            )

            required[key] = (
                required.get(
                    key,
                    Decimal("0"),
                )
                + ingredient.quantity
            )

    return required


def get_pantry_quantities(
    pantry_items,
) -> dict[tuple[str, str], Decimal]:

    available: dict[
        tuple[str, str],
        Decimal,
    ] = {}

    for item in pantry_items:
        ingredient_name = normalize_ingredient(
            item.ingredient
        )

        unit = item.unit.strip().lower()

        key = (
            ingredient_name,
            unit,
        )

        available[key] = (
            available.get(
                key,
                Decimal("0"),
            )
            + item.quantity
        )

    return available


def calculate_grocery_list(
    meal_plan_entries,
    pantry_items,
    start_date: date,
    end_date: date,
) -> GroceryListResponse:

    required = aggregate_required_ingredients(
        meal_plan_entries
    )

    pantry = get_pantry_quantities(
        pantry_items
    )

    items: list[GroceryListItem] = []

    for (
        ingredient,
        unit,
    ), required_quantity in required.items():

        pantry_quantity = pantry.get(
            (ingredient, unit),
            Decimal("0"),
        )

        quantity_to_buy = (
            required_quantity
            - pantry_quantity
        )

        if quantity_to_buy <= Decimal("0"):
            continue

        items.append(
            GroceryListItem(
                ingredient=ingredient,
                unit=unit,
                required_quantity=required_quantity,
                pantry_quantity=pantry_quantity,
                quantity_to_buy=quantity_to_buy,
            )
        )

    items.sort(
        key=lambda item: item.ingredient
    )

    return GroceryListResponse(
        start_date=start_date,
        end_date=end_date,
        items=items,
    )


def get_grocery_list(
    db: Session,
    profile_id: UUID,
    start_date: date,
    end_date: date,
) -> GroceryListResponse:

    meal_plan_entries = (
        meal_plan_repository.get_meal_plan_entries(
            db,
            profile_id,
            start_date,
            end_date,
        )
    )

    pantry_items = (
        pantry_repository.get_pantry_items(
            db,
            profile_id,
        )
    )

    return calculate_grocery_list(
        meal_plan_entries,
        pantry_items,
        start_date,
        end_date,
    )