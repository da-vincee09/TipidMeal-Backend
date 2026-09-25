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

from features.ingredients.models.ingredient_price import IngredientPrice
from features.ingredients.models.ingredient import Ingredient

from features.recommendations.utils import (
    normalize_ingredient,
)

from features.ingredients.repository import convert_quantity


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


def get_ingredient_price_map(
    db: Session,
) -> dict[tuple[str, str], Decimal]:
    """
    (ingredient_name, unit) -> price_per_unit, for every priced
    ingredient. Small table — re-querying per call is fine at this
    scale, matching the same approach used by
    nutrition.get_ingredient_food_group_map().
    """
    rows = (
        db.query(IngredientPrice)
        .join(Ingredient, IngredientPrice.ingredient_id == Ingredient.id)
        .all()
    )

    return {
        (row.ingredient.name, row.unit.strip().lower()): row.price_per_unit
        for row in rows
    }


def calculate_grocery_list(
    db: Session,
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

    price_map = get_ingredient_price_map(db)

    items: list[GroceryListItem] = []
    total_cost = Decimal("0")
    has_any_priced_item = False

    for (
        ingredient,
        unit,
    ), required_quantity in required.items():

        pantry_quantity = pantry.get(
            (ingredient, unit),
            Decimal("0"),
        )

        # No exact-unit match in pantry — check whether the pantry
        # holds this same ingredient under a DIFFERENT, but convertible,
        # unit (e.g. pantry has "rice: 2 kg", requirement is "rice: 500 g").
        # Sums across all convertible pantry entries for this ingredient,
        # since a user might have separate pantry rows in different units.
        if pantry_quantity == Decimal("0"):
            for (pantry_ingredient, pantry_unit), pantry_qty in pantry.items():
                if pantry_ingredient != ingredient or pantry_unit == unit:
                    continue
                converted = convert_quantity(db, pantry_qty, pantry_unit, unit)
                if converted is not None:
                    pantry_quantity += converted

        quantity_to_buy = (
            required_quantity
            - pantry_quantity
        )

        if quantity_to_buy <= Decimal("0"):
            continue

        price_per_unit = price_map.get((ingredient, unit))

        estimated_cost = None
        if price_per_unit is not None:
            estimated_cost = (quantity_to_buy * price_per_unit).quantize(Decimal("0.01"))
            total_cost += estimated_cost
            has_any_priced_item = True

        items.append(
            GroceryListItem(
                ingredient=ingredient,
                unit=unit,
                required_quantity=required_quantity,
                pantry_quantity=pantry_quantity,
                quantity_to_buy=quantity_to_buy,
                estimated_cost=estimated_cost,
            )
        )

    items.sort(
        key=lambda item: item.ingredient
    )

    return GroceryListResponse(
        start_date=start_date,
        end_date=end_date,
        items=items,
        total_estimated_cost=total_cost.quantize(Decimal("0.01")) if has_any_priced_item else None,
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
        db,
        meal_plan_entries,
        pantry_items,
        start_date,
        end_date,
    )