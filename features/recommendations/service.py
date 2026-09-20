from sqlalchemy.orm import Session
from decimal import Decimal
from features.meals.models import Meal
from features.pantry.models import PantryItem
from features.recommendations.utils import normalize_ingredient
from features.recommendations.tfidf import MealTfidfEngine
from features.recommendations.rules import (
    adapt_meal,
    get_effective_available_ingredients,
)
from features.recommendations.scoring import (
    calculate_budget_score,
    calculate_skill_score,
    calculate_allergy_score,
    calculate_disliked_ingredient_score,
    calculate_hybrid_score,
)
from features.profiles.models.profile import Profile


def get_recommendation_data(db: Session, profile_id):
    meals = db.query(Meal).all()

    pantry_items = (
        db.query(PantryItem)
        .filter(PantryItem.profile_id == profile_id)
        .all()
    )

    return meals, pantry_items


def get_available_ingredients(
    pantry_items,
) -> dict[str, dict[str, Decimal]]:
    available: dict[str, dict[str, Decimal]] = {}

    for item in pantry_items:
        name = normalize_ingredient(item.ingredient)
        unit = item.unit.strip().lower()

        available.setdefault(name, {})
        available[name][unit] = (
            available[name].get(unit, Decimal("0")) + item.quantity
        )

    return available


def calculate_meal_coverage(
    db: Session,
    profile_id,
    sort_by: str = "score",
):
    profile = (
        db.query(Profile)
        .filter(Profile.id == profile_id)
        .first()
    )

    if profile is None:
        return []

    meals, pantry_items = get_recommendation_data(
        db,
        profile_id,
    )

    if not meals:
        return []

    available_ingredients = get_available_ingredients(
        pantry_items
    )

    engine = MealTfidfEngine()
    engine.fit(meals)

    recommendations = []

    for index, meal in enumerate(meals):

        # 1. Affordability gate — hard requirement, independent of
        #    pantry match. A meal the user can't afford is never
        #    recommended, no matter how well it adapts from pantry.
        is_affordable = float(meal.estimated_cost) <= float(profile.daily_budget)

        if not is_affordable:
            continue

        # 2. Determine pantry adaptation — no longer gates inclusion,
        #    only informs tiering/display (see sort step below).
        adaptation = adapt_meal(
            db,
            meal.ingredients,
            available_ingredients,
        )

        # 3. Calculate effective ingredients after substitutions.
        effective_ingredients = (
            get_effective_available_ingredients(
                db,
                meal.ingredients,
                available_ingredients,
            )
        )

        # 4. Calculate pantry ingredient coverage.
        coverage = (
            engine.calculate_weighted_ingredient_coverage(
                index,
                effective_ingredients,
            )
        )

        meal_ingredients = [
            ingredient.ingredient
            for ingredient in meal.ingredients
        ]

        # 5. Get user's allergies.
        allergies = [
            allergy.allergy
            for allergy in profile.food_allergies
        ]

        # 6. Get user's disliked ingredients.
        disliked_ingredients = [
            disliked.ingredient
            for disliked in profile.disliked_ingredients
        ]

        # 7. Calculate individual scores.
        budget_score = calculate_budget_score(
            float(meal.estimated_cost),
            float(profile.daily_budget),
        )

        skill_score = calculate_skill_score(
            profile.cooking_skill_level,
            meal.difficulty,
        )

        allergy_score = calculate_allergy_score(
            meal_ingredients,
            allergies,
        )

        disliked_score = (
            calculate_disliked_ingredient_score(
                meal_ingredients,
                disliked_ingredients,
            )
        )

        # 8. Never recommend a meal containing an allergen —
        #    hard filter, unchanged.
        if allergy_score == 0.0:
            continue

        # 9. Calculate final hybrid score.
        hybrid_score = calculate_hybrid_score(
            float(coverage),
            budget_score,
            skill_score,
            allergy_score,
            disliked_score,
        )

        recommendations.append(
            {
                "meal": meal,
                "coverage": coverage,
                "budget_score": budget_score,
                "skill_score": skill_score,
                "allergy_score": allergy_score,
                "disliked_score": disliked_score,
                "hybrid_score": hybrid_score,
                "adaptation": adaptation,
            }
        )

    if sort_by == "cost":
        recommendations.sort(
            key=lambda item: (
                item["meal"].estimated_cost,
                -item["hybrid_score"],
            )
        )
    else:
        # Default "score" sort: tier good pantry match ("adapt")
        # ahead of "fallback" — everything here is already affordable —
        # then hybrid score breaks ties within each tier.
        recommendations.sort(
            key=lambda item: (
                item["adaptation"]["decision"] != "adapt",
                -item["hybrid_score"],
            )
        )

    return recommendations