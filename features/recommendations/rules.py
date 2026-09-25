from decimal import Decimal

from features.recommendations.utils import normalize_ingredient
from features.recommendations.models import IngredientSubstitution
from features.ingredients.models.ingredient import Ingredient
from features.ingredients.repository import convert_quantity

def is_ingredient_available(
    ingredient: str,
    available_ingredients: dict[str, dict[str, Decimal]],
) -> bool:
    normalized = normalize_ingredient(ingredient)

    return normalized in available_ingredients


def get_pantry_quantity(
    db,
    ingredient: str,
    unit: str,
    available_ingredients: dict[str, dict[str, Decimal]],
) -> Decimal | None:
    """Returns the total pantry quantity for this ingredient, converted
    into the given unit if necessary. Returns None only if the
    ingredient isn't in the pantry at all, or is present only under
    unit(s) with no known conversion path to the requested unit
    (e.g. pantry has "pcs" but recipe needs "g").
    """
    normalized_name = normalize_ingredient(ingredient)
    normalized_unit = unit.strip().lower()

    pantry_units = available_ingredients.get(normalized_name)
    if pantry_units is None:
        return None

    # Exact unit match — no conversion needed.
    if normalized_unit in pantry_units:
        return pantry_units[normalized_unit]

    # Try converting from any unit the pantry actually has for this
    # ingredient. Sum all convertible quantities together (e.g. pantry
    # has both "500 g" AND "1 kg" of rice under separate entries —
    # both should count toward a "700 g" requirement).
    total_converted = Decimal("0")
    found_any_conversion = False

    for pantry_unit, pantry_quantity in pantry_units.items():
        converted = convert_quantity(db, pantry_quantity, pantry_unit, normalized_unit)
        if converted is not None:
            total_converted += converted
            found_any_conversion = True

    if found_any_conversion:
        return total_converted

    return None


def classify_ingredients(
    ingredients,
    available_ingredients: dict[str, dict[str, Decimal]],
) -> dict[str, list[str]]:
    available = []
    unavailable = []

    for ingredient in ingredients:
        name = ingredient.ingredient

        if is_ingredient_available(
            name,
            available_ingredients,
        ):
            available.append(name)
        else:
            unavailable.append(name)

    return {
        "available": available,
        "unavailable": unavailable,
    }


def get_substitute(
    db,
    ingredient: str,
) -> str | None:
    normalized = normalize_ingredient(ingredient)

    # IngredientSubstitution.ingredient/.substitute are read-only
    # Python properties (name resolved through ingredient_ref/
    # substitute_ref), not mapped columns — they can't be used in a
    # .filter() query-time comparison. Look up the Ingredient row by
    # name first, then filter IngredientSubstitution by its real
    # mapped column, ingredient_id.
    ingredient_row = (
        db.query(Ingredient)
        .filter(Ingredient.name == normalized)
        .first()
    )

    if ingredient_row is None:
        return None

    substitution = (
        db.query(IngredientSubstitution)
        .filter(IngredientSubstitution.ingredient_id == ingredient_row.id)
        .first()
    )

    if substitution is None:
        return None

    return substitution.substitute  # property shim -> substitute_ref.name


def get_effective_available_ingredients(
    db,
    ingredients,
    available_ingredients: dict[str, dict[str, Decimal]],
) -> set[str]:
    # Name-only set for TF-IDF coverage — quantity sufficiency is a
    # separate, per-ingredient concern handled in adapt_ingredient below,
    # not part of coverage scoring.
    effective = set(available_ingredients)

    for ingredient in ingredients:
        normalized = normalize_ingredient(
            ingredient.ingredient
        )

        if normalized in effective:
            continue

        substitute = get_substitute(
            db,
            normalized,
        )

        if substitute is None:
            continue

        normalized_substitute = normalize_ingredient(
            substitute
        )

        if normalized_substitute in available_ingredients:
            effective.add(normalized)

    return effective


def adapt_ingredient(
    db,
    ingredient,
    available_ingredients: dict[str, dict[str, Decimal]],
) -> dict:
    name = ingredient.ingredient
    normalized = normalize_ingredient(name)
    required_unit = ingredient.unit.strip().lower()

    if is_ingredient_available(
        normalized,
        available_ingredients,
    ):
        pantry_quantity = get_pantry_quantity(
            db,
            normalized,
            required_unit,
            available_ingredients,
        )

        if pantry_quantity is None:
            return {
                "ingredient": name,
                "action": "retain",
                "replacement": None,
            }

        if pantry_quantity >= ingredient.quantity:
            return {
                "ingredient": name,
                "action": "retain",
                "replacement": None,
            }

        return {
            "ingredient": name,
            "action": "insufficient",
            "replacement": None,
            "available_quantity": pantry_quantity,
            "required_quantity": ingredient.quantity,
            "unit": required_unit,
        }

    substitute = get_substitute(
        db,
        normalized,
    )

    if substitute is not None:
        normalized_substitute = normalize_ingredient(
            substitute
        )

        if is_ingredient_available(
            normalized_substitute,
            available_ingredients,
        ):
            return {
                "ingredient": name,
                "action": "substitute",
                "replacement": substitute,
            }

    if ingredient.is_optional:
        return {
            "ingredient": name,
            "action": "omit",
            "replacement": None,
        }

    return {
        "ingredient": name,
        "action": "unavailable",
        "replacement": None,
    }


def adapt_meal(
    db,
    ingredients,
    available_ingredients: dict[str, dict[str, Decimal]],
) -> dict:
    adaptations = []

    for ingredient in ingredients:
        adaptations.append(
            adapt_ingredient(
                db,
                ingredient,
                available_ingredients,
            )
        )

    has_unavailable = any(
        item["action"] == "unavailable"
        for item in adaptations
    )

    if has_unavailable:
        decision = "fallback"
    else:
        decision = "adapt"

    return {
        "decision": decision,
        "ingredients": adaptations,
    }