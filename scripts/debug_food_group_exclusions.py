"""
Diagnostic: shows, for every meal, which ingredients are counted in the
food-group proportions and which are silently dropped (and why).

Use it to find why a meal's Go/Grow/Glow split looks wrong — e.g. pork
dishes showing 0% Grow. An ingredient is dropped when it has no
ingredient_food_groups entry (name mismatch), or when it is measured in
a unit with no gram conversion in INGREDIENT_GRAM_CONVERSIONS.

Run from the backend project root, inside the venv:
    python -m scripts.debug_food_group_exclusions
    python -m scripts.debug_food_group_exclusions sinigang   # filter by name
"""

import sys
from collections import Counter

from core.database import SessionLocal
from features.meals.models.meal import Meal
from features.nutrition.constants import convert_to_grams
from features.nutrition.service import get_ingredient_food_group_map


def run(name_filter: str | None = None):
    db = SessionLocal()
    try:
        food_group_map = get_ingredient_food_group_map(db)
        meals = db.query(Meal).order_by(Meal.name).all()

        reasons = Counter()

        for meal in meals:
            if name_filter and name_filter.lower() not in meal.name.lower():
                continue

            print(f"\n{meal.name}")
            for ing in meal.ingredients:
                key = ing.ingredient.strip().lower()
                unit = ing.unit.strip().lower()
                group = food_group_map.get(key)
                label = f"  {ing.quantity} {ing.unit} {ing.ingredient}"

                if group is None:
                    status = "DROPPED - no ingredient_food_groups entry"
                    reasons["no food-group entry"] += 1
                elif group == "other":
                    status = "skipped - classified 'other'"
                    reasons["classified other"] += 1
                else:
                    grams = convert_to_grams(
                        ing.ingredient, ing.unit, ing.quantity
                    )
                    if grams is None:
                        status = (
                            f"DROPPED - {group}, no gram conversion "
                            f"for ({key}, {unit})"
                        )
                        reasons["no gram conversion"] += 1
                    else:
                        status = f"counted - {group}, {float(grams):.0f} g"
                        reasons["counted"] += 1

                print(f"{label}: {status}")

        print("\nSummary:")
        for reason, count in reasons.most_common():
            print(f"  {reason}: {count}")
    finally:
        db.close()


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)