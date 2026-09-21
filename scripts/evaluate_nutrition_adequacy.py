"""
Week 8, Day 6 — Objective 4 evaluation harness.

Builds a (age_bracket, sex, activity_level) x meal test-case matrix,
runs the real nutritional adequacy computation for every combination,
and reports the accuracy metric that goes into the thesis results
chapter under Objective 4.

Scoring is ulam-only (see features/nutrition/constants.py): staple
meals such as Garlic Fried Rice are reported as not applicable and are
excluded from the accuracy denominator, and the breakdown below shows
how much each criterion (calories vs. food groups) contributes.

Run from the backend project root, inside the venv:
    python -m scripts.evaluate_nutrition_adequacy
"""

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from core.database import SessionLocal
from features.meals.models.meal import Meal
from features.nutrition.service import compute_nutritional_adequacy


@dataclass
class EvalProfile:
    """
    Minimal stand-in for a Profile row. compute_caloric_adequacy only
    reads date_of_birth/sex/physical_activity_level, so a lightweight
    object is enough — no need to persist real Profile rows for this.
    """
    label: str  # human-readable, for the CSV/report
    date_of_birth: date
    sex: str
    physical_activity_level: str


# Representative age used per PDRI bracket (roughly bracket midpoint).
# The exact day-of-birth doesn't matter — only that calculate_age()
# lands back in the intended bracket.
_AGE_BRACKET_REPRESENTATIVE_AGE = {
    "19-29": 24,
    "30-49": 40,
    "50-59": 55,
    "60-69": 65,
    "70+": 75,
}

_SEXES = ["male", "female"]
_ACTIVITY_LEVELS = ["sedentary", "moderately_active", "active"]


def _years_ago(today: date, years: int) -> date:
    try:
        return today.replace(year=today.year - years)
    except ValueError:  # Feb 29 -> non-leap year
        return today.replace(year=today.year - years, day=28)


def build_test_profiles() -> list[EvalProfile]:
    today = date.today()
    profiles = []
    for bracket, age in _AGE_BRACKET_REPRESENTATIVE_AGE.items():
        dob = _years_ago(today, age)
        for sex in _SEXES:
            for activity in _ACTIVITY_LEVELS:
                profiles.append(
                    EvalProfile(
                        label=f"{sex}-{bracket}-{activity}",
                        date_of_birth=dob,
                        sex=sex,
                        physical_activity_level=activity,
                    )
                )
    return profiles


def run_evaluation():
    db = SessionLocal()
    try:
        meals = db.query(Meal).order_by(Meal.name).all()
        profiles = build_test_profiles()

        results = []
        for profile in profiles:
            for meal in meals:
                outcome = compute_nutritional_adequacy(db, meal, profile)
                results.append(
                    {
                        "profile": profile.label,
                        "meal": meal.name,
                        "meal_calories": meal.calories,
                        "is_staple": outcome["is_staple"],
                        "caloric_adequacy": outcome["caloric_adequacy"],
                        "food_group_proportions": outcome[
                            "food_group_proportions"
                        ],
                        "food_group_adequate": outcome["food_group_adequate"],
                        "nutritionally_adequate": outcome[
                            "nutritionally_adequate"
                        ],
                    }
                )

        # Only test cases with a determinate answer count toward the
        # denominator — a case that's structurally "unavailable"
        # (a staple meal, or an unclassifiable meal) isn't a pass or a
        # fail, it's not evaluable, so it's excluded rather than
        # silently counted against the accuracy figure either way.
        staples = [r for r in results if r["is_staple"]]
        evaluated = [
            r for r in results if r["nutritionally_adequate"] is not None
        ]
        other_unavailable = (
            len(results) - len(staples) - len(evaluated)
        )
        adequate = [
            r for r in evaluated if r["nutritionally_adequate"] is True
        ]
        accuracy = len(adequate) / len(evaluated) if evaluated else 0.0

        calorie_counts = Counter(r["caloric_adequacy"] for r in evaluated)
        food_group_pass = sum(
            1 for r in evaluated if r["food_group_adequate"] is True
        )

        print(f"Total test cases generated: {len(results)}")
        print(f"  Staple-meal cases (not applicable): {len(staples)}")
        print(f"  Other not-evaluable cases: {other_unavailable}")
        print(f"Evaluable test cases: {len(evaluated)}")
        print()
        print("Breakdown of evaluable cases:")
        for verdict in ("within", "below", "above"):
            count = calorie_counts.get(verdict, 0)
            print(f"  Calories {verdict}: {count} ({count / len(evaluated):.1%})"
                  if evaluated else f"  Calories {verdict}: 0")
        if evaluated:
            print(
                f"  Food groups adequate: {food_group_pass} "
                f"({food_group_pass / len(evaluated):.1%})"
            )
        print()
        print(f"Meeting both criteria: {len(adequate)}")
        print(f"Nutritional adequacy accuracy: {accuracy:.2%}")

        # Per-meal view: how many of the evaluable profiles each meal
        # is adequate for. Food-group verdict is identical across
        # profiles, so differences between profiles come from calories.
        per_meal = defaultdict(lambda: [0, 0])  # meal -> [adequate, evaluable]
        for r in evaluated:
            per_meal[r["meal"]][1] += 1
            if r["nutritionally_adequate"] is True:
                per_meal[r["meal"]][0] += 1
        print()
        print("Per-meal adequacy (adequate profiles / evaluable profiles):")
        for meal_name, (ok, total) in sorted(per_meal.items()):
            print(f"  {meal_name}: {ok}/{total}")

        output_path = Path("nutrition_evaluation_results.csv")
        with output_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "profile",
                    "meal",
                    "meal_calories",
                    "is_staple",
                    "caloric_adequacy",
                    "food_group_proportions",
                    "food_group_adequate",
                    "nutritionally_adequate",
                ],
            )
            writer.writeheader()
            writer.writerows(results)

        print()
        print(f"Full results written to {output_path.resolve()}")

    finally:
        db.close()


if __name__ == "__main__":
    run_evaluation()