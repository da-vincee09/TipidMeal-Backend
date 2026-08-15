def normalize_ingredient(value: str) -> str:
    return "_".join(value.strip().lower().split())


def meal_to_document(ingredients) -> str:
    return " ".join(
        normalize_ingredient(ingredient.ingredient)
        for ingredient in ingredients
    )