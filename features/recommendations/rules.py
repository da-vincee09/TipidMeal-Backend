from features.recommendations.utils import normalize_ingredient
from features.recommendations.models import IngredientSubstitution


def is_ingredient_available(
    ingredient: str,
    available_ingredients: set[str],
) -> bool:
    normalized = normalize_ingredient(ingredient)

    return normalized in available_ingredients


def classify_ingredients(
    ingredients,
    available_ingredients: set[str],
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
    available_ingredients: set[str],
) -> set[str]:
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
    available_ingredients: set[str],
) -> dict:
    name = ingredient.ingredient
    normalized = normalize_ingredient(name)

    if is_ingredient_available(
        normalized,
        available_ingredients,
    ):
        return {
            "ingredient": name,
            "action": "retain",
            "replacement": None,
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
    available_ingredients: set[str],
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