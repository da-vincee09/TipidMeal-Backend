def calculate_budget_score(
    meal_cost: float,
    budget_per_meal: float,
) -> float:

    if budget_per_meal <= 0:
        return 0.0

    ratio = meal_cost / budget_per_meal

    if ratio <= 0.50:
        return 1.00

    if ratio <= 0.75:
        return 0.90

    if ratio <= 1.00:
        return 0.80

    if ratio <= 1.25:
        return 0.50

    return 0.00


def calculate_skill_score(
    user_skill: str,
    meal_difficulty: str,
) -> float:

    skill = user_skill.strip().lower()
    difficulty = meal_difficulty.strip().lower()

    compatibility = {
        "beginner": {
            "easy": 1.00,
            "medium": 0.60,
            "hard": 0.20,
        },
        "intermediate": {
            "easy": 1.00,
            "medium": 1.00,
            "hard": 0.60,
        },
        "advanced": {
            "easy": 1.00,
            "medium": 1.00,
            "hard": 1.00,
        },
    }

    return compatibility.get(
        skill,
        {},
    ).get(
        difficulty,
        0.0,
    )


def calculate_allergy_score(
    meal_ingredients: list[str],
    allergy_ingredients: set[str],
) -> float:
    """
    allergy_ingredients is the EXPANDED set of actual ingredient names
    the profile is allergic to (already resolved from allergy category
    names like "Shellfish" via allergen_categories) — not the raw
    category strings themselves.
    """

    normalized_ingredients = {
        ingredient.strip().lower()
        for ingredient in meal_ingredients
    }

    normalized_allergy_ingredients = {
        ingredient.strip().lower()
        for ingredient in allergy_ingredients
    }

    if normalized_ingredients.intersection(
        normalized_allergy_ingredients
    ):
        return 0.0

    return 1.0


def calculate_disliked_ingredient_score(
    meal_ingredients: list[str],
    disliked_ingredients: list[str],
) -> float:

    normalized_ingredients = {
        ingredient.strip().lower()
        for ingredient in meal_ingredients
    }

    normalized_disliked = {
        ingredient.strip().lower()
        for ingredient in disliked_ingredients
    }

    disliked_count = len(
        normalized_ingredients.intersection(
            normalized_disliked
        )
    )

    if disliked_count == 0:
        return 1.00

    if disliked_count == 1:
        return 0.90

    if disliked_count == 2:
        return 0.80

    return 0.70


def calculate_hybrid_score(
    coverage: float,
    budget_score: float,
    skill_score: float,
    allergy_score: float,
    disliked_score: float,
) -> float:

    return (
        coverage * 0.30
        + budget_score * 0.30
        + skill_score * 0.10
        + allergy_score * 0.20
        + disliked_score * 0.10
    )