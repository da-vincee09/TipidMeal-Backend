"""
Nutrition adequacy computation (Week 8, Objective 4).

Two independent checks are combined into one verdict:

1. Caloric adequacy — the meal's calories vs. the per-meal bracket
   derived from the profile's daily requirement (PDRI x activity).
2. Food-group adequacy — the meal's Grow/Glow balance vs. the
   Pinggang Pinoy bands.

Seeded Meals are ulam-only dishes, so both checks are scaled to an
ulam rather than a full plate (see constants.py, "Ulam-only scoring").
Staple Meals (e.g. Garlic Fried Rice) are not judged as an ulam: they
report is_staple=True with no verdict, rather than a false "fail".

Two-tier unavailability design: a meal whose ingredients can't be
classified/measured at all has no proportions (None), and any None on
either side makes nutritionally_adequate None rather than False.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from features.ingredients.models.ingredient import Ingredient

from features.meals.models.meal import Meal
from features.nutrition.constants import (
    ULAM_FOOD_GROUP_TARGETS,
    convert_to_grams,
    get_daily_caloric_requirement,
    get_per_meal_bracket,
    is_staple_meal,
)
from features.nutrition.models.ingredient_food_group import IngredientFoodGroup
from features.profiles.models.profile import Profile


_food_group_map_cache: dict[str, str] | None = None


def get_ingredient_food_group_map(db: Session, refresh: bool = False) -> dict[str, str]:
    """Ingredient name -> food group, loaded once per process."""
    global _food_group_map_cache
    if _food_group_map_cache is None or refresh:
        rows = (
            db.query(Ingredient.name, IngredientFoodGroup.food_group)
            .join(IngredientFoodGroup, IngredientFoodGroup.ingredient_id == Ingredient.id)
            .all()
        )
        _food_group_map_cache = {name.strip().lower(): group for name, group in rows}
    return _food_group_map_cache


def compute_caloric_adequacy(meal: Meal, profile: Profile) -> str:
    """
    Returns "within" | "below" | "above" | "unavailable".

    "unavailable" covers: physical_activity_level not set, a sex value
    with no PDRI row (e.g. "Prefer not to say"), or the meal itself
    having no calories value. (Ages below 19 are clamped to the 19-29
    bracket rather than treated as unavailable.)
    Per Week 8 Part 3 item 8, this is deliberately NOT treated as a
    false "not adequate" — callers must handle it as its own state.
    """
    if meal.calories is None:
        return "unavailable"

    requirement = get_daily_caloric_requirement(
        profile.date_of_birth,
        profile.sex,
        profile.physical_activity_level,
    )

    if not requirement.is_ok:
        return "unavailable"

    lower, upper = get_per_meal_bracket(requirement.daily_kcal)

    if meal.calories < lower:
        return "below"
    if meal.calories > upper:
        return "above"
    return "within"


def compute_food_group_proportions(
    db: Session,
    meal: Meal,
) -> dict[str, float] | None:
    """
    Returns {"go": %, "grow": %, "glow": %} by ingredient quantity
    (grams), or None if the meal has no ingredients whose mass could
    be classified and measured at all (whole-meal "unclassifiable"
    fallback — see module docstring above for the two-tier design).

    These are the meal's raw shares across all three groups. The
    ulam-only verdict is derived from them in
    compute_food_group_adequate().
    """
    food_group_map = get_ingredient_food_group_map(db)

    grams_by_group: dict[str, Decimal] = {
        "go": Decimal("0"),
        "grow": Decimal("0"),
        "glow": Decimal("0"),
    }

    for ingredient in meal.ingredients:
        name_key = ingredient.ingredient.strip().lower()
        group = food_group_map.get(name_key)

        # Unclassified ingredient (no ingredient_food_groups entry) or
        # explicitly "other" (condiment/spice/fat) — excluded from the
        # denominator either way, per Week 8 Part 2.
        if group is None or group == "other":
            continue

        grams = convert_to_grams(
            ingredient.ingredient,
            ingredient.unit,
            ingredient.quantity,
        )

        # No known gram conversion for this (ingredient, unit) pair —
        # excluded from this meal's proportions rather than guessed.
        if grams is None:
            continue

        grams_by_group[group] += grams

    total_grams = sum(grams_by_group.values())

    if total_grams == 0:
        return None

    return {
        group: round(float((grams / total_grams) * 100), 1)
        for group, grams in grams_by_group.items()
    }


def compute_food_group_adequate(
    proportions: dict[str, float] | None,
) -> bool | None:
    """
    Ulam-only food-group verdict.

    Go is ignored (the staple is supplied by a separate Meal). Grow and
    Glow are renormalized to shares of the Grow+Glow total, then
    checked against ULAM_FOOD_GROUP_TARGETS (inclusive of the
    boundary). The two shares sum to 100%, so their bands are mirror
    images; both are checked anyway to keep the intent explicit.

    Returns None if proportions are unavailable (meal unclassifiable)
    or the meal has no Grow/Glow content to assess at all — not a
    false "fail".

    Note: renormalizing from proportions that were already rounded to
    1 decimal can move a share by up to ~0.1 percentage point, which
    only matters for a meal sitting exactly on a band boundary.
    """
    if proportions is None:
        return None

    grow = proportions["grow"]
    glow = proportions["glow"]
    ulam_total = grow + glow

    if ulam_total == 0:
        return None

    shares = {
        "grow": (grow / ulam_total) * 100,
        "glow": (glow / ulam_total) * 100,
    }

    for group, (min_pct, max_pct) in ULAM_FOOD_GROUP_TARGETS.items():
        if not (min_pct <= shares[group] <= max_pct):
            return False

    return True


def compute_nutritional_adequacy(
    db: Session,
    meal: Meal,
    profile: Profile,
) -> dict:
    """
    Combined result per Week 8 Part 3, item 8's shape, plus is_staple.

    nutritionally_adequate is None (not False) whenever either half of
    the computation is itself unavailable — this preserves the "don't
    silently report a false negative" principle from Part 3, item 8,
    extended consistently to the food-group side even though the doc's
    example JSON only spells it out for caloric_adequacy.

    Staple meals (is_staple=True) are not judged as an ulam: caloric
    adequacy is "unavailable" and both adequacy verdicts are None. The
    raw proportions are still returned for display.
    """
    food_group_proportions = compute_food_group_proportions(db, meal)

    if is_staple_meal(meal.name):
        return {
            "caloric_adequacy": "unavailable",
            "food_group_proportions": food_group_proportions,
            "food_group_adequate": None,
            "nutritionally_adequate": None,
            "is_staple": True,
        }

    caloric_adequacy = compute_caloric_adequacy(meal, profile)
    food_group_adequate = compute_food_group_adequate(food_group_proportions)

    if caloric_adequacy == "unavailable" or food_group_adequate is None:
        nutritionally_adequate = None
    else:
        nutritionally_adequate = (
            caloric_adequacy == "within" and food_group_adequate
        )

    return {
        "caloric_adequacy": caloric_adequacy,
        "food_group_proportions": food_group_proportions,
        "food_group_adequate": food_group_adequate,
        "nutritionally_adequate": nutritionally_adequate,
        "is_staple": False,
    }