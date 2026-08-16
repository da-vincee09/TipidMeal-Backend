from decimal import Decimal

from features.recommendations.utils import normalize_ingredient
from features.recommendations.models import IngredientSubstitution


def is_ingredient_available(
    ingredient: str,
    available_ingredients: dict[str, dict[str, Decimal]],
) -> bool:
    normalized = normalize_ingredient(ingredient)

    return normalized in available_ingredients


def get_pantry_quantity(
    ingredient: str,
    unit: str,
    available_ingredients: dict[str, dict[str, Decimal]],
) -> Decimal | None:
    """Returns the total pantry quantity for this ingredient **in the
    given unit**, or None if the ingredient isn't in the pantry under
    that exact unit (either missing entirely, or present under a
    different, non-comparable unit).
    """
    normalized_name = normalize_ingredient(ingredient)
    normalized_unit = unit.strip().lower()

    return available_ingredients.get(normalized_name, {}).get(
        normalized_unit
    )


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

    substitution = (
        db.query(IngredientSubstitution)
        .filter(
            IngredientSubstitution.ingredient == normalized
        )
        .first()
    )

    if substitution is None:
        return None

    return substitution.substitute


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
            normalized,
            required_unit,
            available_ingredients,
        )

        # Units don't align (e.g. pantry has "pcs", recipe needs "g") —
        # we can't safely compare without a conversion table, so we
        # assume availability rather than block the meal on a
        # comparison we can't actually make.
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

        # Same unit, but not enough of it. Doesn't trigger fallback —
        # this is informational so the UI can show the shortfall.
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

    # Only a true "unavailable" (no substitute, not optional) triggers
    # fallback. "insufficient" is a soft warning, not a blocker — the
    # user does own the ingredient, just not enough of it, and we're
    # not confident enough in raw quantity math to reject a whole meal
    # over it.
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