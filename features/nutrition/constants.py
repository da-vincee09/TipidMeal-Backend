"""
Static reference data for the Nutrition feature (Week 8, Objective 4).

Two external standards are combined here, and that combination is itself
a methodological choice — not a literal single official table — so it's
documented explicitly rather than silently baked in:

1. PDRI (Philippine Dietary Reference Intakes) 2015, Revised Sept 2018
   — FNRI-DOST. Recommended Energy Intake by sex + age bracket.
   Source: "Philippine Dietary Reference Intakes 2015: Summary Tables",
   FNRI-DOST (fnri.dost.gov.ph). This table gives ONE value per
   (sex, age) — it does not stratify by physical activity level.

2. FAO/WHO/UNU (2001), "Human Energy Requirements: Report of a Joint
   Expert Consultation", Table 5.3 — Physical Activity Level (PAL)
   categories, used here to scale the PDRI (sex, age) value up/down
   for activity level, anchored on "moderately_active" = the PDRI
   value as-is.

This composite approach must be documented as such in the thesis
methodology chapter, with both sources cited separately.

Ulam-only scoring (a third methodological choice)
-------------------------------------------------
Seeded Meals are ulam/viand dishes; rice and other Go-group staples are
modeled as their own separate Meals. Both Part 1's per-meal calorie
target and Pinggang Pinoy's food-group bands describe a WHOLE plate
(staple + ulam), so each is rescaled to represent the ulam alone:

- Calories: bracket scaled by ULAM_ENERGY_SHARE (see below).
- Food groups: Go is excluded, and the Grow/Glow bands are divided by
  the same share (ULAM_FOOD_GROUP_TARGETS), i.e. judged as a share of
  the Grow+Glow total.
- Staple Meals (STAPLE_MEAL_NAMES) are not judged as an ulam at all.

ULAM_ENERGY_SHARE, ULAM_FOOD_GROUP_TARGETS and STAPLE_MEAL_NAMES are
app-specific reconciliations, not official PDRI or Pinggang Pinoy
figures — document them as such in the methodology chapter.
"""

from datetime import date
from decimal import Decimal


# ── FAO/WHO/UNU (2001) PAL midpoints, Table 5.3 ───────────────────────
# Used only as RATIOS relative to the "moderately_active" midpoint,
# to scale the PDRI baseline. Not used as literal PAL multipliers
# against BMR (we don't compute BMR — we scale directly off PDRI's
# already-computed REI value).
_PAL_MIDPOINTS = {
    "sedentary": Decimal("1.55"),          # range 1.40-1.69
    "moderately_active": Decimal("1.85"),  # range 1.70-1.99 (anchor)
    "active": Decimal("2.20"),             # range 2.00-2.40
}

_ACTIVITY_SCALE_FACTOR = {
    level: (midpoint / _PAL_MIDPOINTS["moderately_active"])
    for level, midpoint in _PAL_MIDPOINTS.items()
}


# ── PDRI 2015 (Rev. 2018) Recommended Energy Intake ───────────────────
# (sex, age_bracket) -> daily kcal, at "moderately_active" (PDRI's own
# unstratified value). age_bracket ranges are PDRI's own groupings,
# not redefined for this app.
#
# Source: FNRI-DOST, "Philippine Dietary Reference Intakes 2015:
# Summary Tables", Revised September 2018.
PDRI_MODERATE_KCAL: dict[tuple[str, str], int] = {
    ("male", "19-29"): 2530,
    ("female", "19-29"): 1930,
    ("male", "30-49"): 2420,
    ("female", "30-49"): 1870,
    ("male", "50-59"): 2420,
    ("female", "50-59"): 1870,
    ("male", "60-69"): 2140,
    ("female", "60-69"): 1610,
    ("male", "70+"): 1960,
    ("female", "70+"): 1540,
}

# Age brackets in ascending order, as (lower_bound_inclusive, label).
# Anyone below 19 has no PDRI adult bracket — see get_age_bracket().
_AGE_BRACKETS: list[tuple[int, str]] = [
    (19, "19-29"),
    (30, "30-49"),
    (50, "50-59"),
    (60, "60-69"),
    (70, "70+"),
]


def get_age_bracket(age_years: int) -> str | None:
    """
    Maps an age in years to a PDRI age bracket label.

    Returns None for age < 19 (no adult PDRI bracket exists for this
    case). Callers must handle None explicitly rather than assume a
    bracket always exists — see get_daily_caloric_requirement().
    """
    bracket = None
    for lower_bound, label in _AGE_BRACKETS:
        if age_years >= lower_bound:
            bracket = label
        else:
            break
    return bracket


def calculate_age(date_of_birth: date, as_of: date | None = None) -> int:
    """Age in whole years as of `as_of` (defaults to today)."""
    today = as_of or date.today()
    age = today.year - date_of_birth.year
    had_birthday_this_year = (today.month, today.day) >= (
        date_of_birth.month,
        date_of_birth.day,
    )
    if not had_birthday_this_year:
        age -= 1
    return age


class CaloricRequirementResult:
    """
    Result of get_daily_caloric_requirement(). Explicit result object
    rather than a bare int/None, so callers can distinguish "activity
    level not set" from "sex value with no PDRI row" from a real
    successful computation — each needs different UI handling.

    Ages below 19 are not a failure state: they are clamped to the
    19-29 bracket (see get_daily_caloric_requirement()).
    """

    def __init__(
        self,
        status: str,  # "ok" | "activity_not_set" | "sex_not_supported"
        daily_kcal: int | None = None,
    ):
        self.status = status
        self.daily_kcal = daily_kcal

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"


def get_daily_caloric_requirement(
    date_of_birth: date,
    sex: str,
    physical_activity_level: str | None,
) -> CaloricRequirementResult:
    """
    Computes daily caloric requirement (kcal) for a profile, per
    Week 8 Part 1, item 3.

    Returns a CaloricRequirementResult rather than raising or
    returning None on failure, so the caller (service.py) can surface
    a clear "unavailable" state rather than a silent default or an
    exception.
    """
    if not physical_activity_level:
        return CaloricRequirementResult(status="activity_not_set")

    age = calculate_age(date_of_birth)
    bracket = get_age_bracket(age)

    if bracket is None:
        # Below 19 — no PDRI adult bracket. Clamped to youngest
        # bracket (19-29) as the documented fallback, rather than a
        # silent guess or a crash. Flag this choice for adviser
        # review if precise pediatric handling matters later.
        bracket = "19-29"

    sex_key = sex.strip().lower()
    if sex_key not in ("male", "female"):
        # PDRI table only has male/female columns. Anything else
        # (e.g. "Prefer not to say") has no PDRI row to look up.
        return CaloricRequirementResult(status="sex_not_supported")

    baseline = PDRI_MODERATE_KCAL.get((sex_key, bracket))
    if baseline is None:
        return CaloricRequirementResult(status="sex_not_supported")

    activity_key = physical_activity_level.strip().lower()
    scale = _ACTIVITY_SCALE_FACTOR.get(activity_key)
    if scale is None:
        return CaloricRequirementResult(status="activity_not_set")

    daily_kcal = round(baseline * scale)
    return CaloricRequirementResult(status="ok", daily_kcal=daily_kcal)


# ── Per-meal caloric bracket (Week 8, Part 1 open decision — resolved) ─
MEALS_PER_DAY = 3
PER_MEAL_TOLERANCE = Decimal("0.20")  # ±20%, confirmed over doc's ±10%

# ── Pinggang Pinoy food-group targets (Week 8, Part 3, item 7) ────────
# (min_pct, max_pct) tolerance bands, per FNRI-DOST Pinggang Pinoy (2016).
# These describe a WHOLE plate. Ulam-only meals are judged against
# ULAM_FOOD_GROUP_TARGETS below instead.
FOOD_GROUP_TARGETS = {
    "go": (23.0, 43.0),
    "grow": (7.0, 27.0),
    "glow": (40.0, 60.0),
}


# ── Ulam-only calorie scaling ──────────────────────────────────────────
# Seeded Meals represent the ulam/viand alone, not a full rice+ulam
# plate (rice is modeled as its own separate Meal, e.g. Garlic Fried
# Rice). So a single dish's calories must be compared against the
# NON-Go share of a full meal's caloric target, not the full target
# itself. Anchored on the midpoint of FOOD_GROUP_TARGETS["go"]
# (23-43%, midpoint 33%) — i.e. the ulam is expected to carry the
# remaining ~67% of a meal's energy, since rice/Go-group staples
# supply the rest. This is an app-specific reconciliation between two
# otherwise-independent parts of this feature, not itself an official
# PDRI or Pinggang Pinoy figure — document it as such in methodology.
_GO_TARGET_MIDPOINT = (
    Decimal(str(sum(FOOD_GROUP_TARGETS["go"]))) / 2
) / 100
ULAM_ENERGY_SHARE = Decimal("1") - _GO_TARGET_MIDPOINT


# ── Ulam-only food-group targets ───────────────────────────────────────
# Go (rice/staples) is supplied by a separate staple Meal, so a
# standalone ulam is judged on Grow and Glow only, measured as a share
# of the Grow+Glow total. Bands are the plate-level FOOD_GROUP_TARGETS
# divided by ULAM_ENERGY_SHARE (the same reconciliation used for the
# calorie bracket), giving roughly Grow 10.4-40.3% and Glow 59.7-89.6%.
# Because the two shares always sum to 100%, the Grow and Glow bands
# are mirror images of each other: passing one means passing the other.
# App-specific, not an official Pinggang Pinoy figure — document as
# such in the methodology chapter.
ULAM_FOOD_GROUP_TARGETS: dict[str, tuple[float, float]] = {
    group: (
        float(Decimal(str(low)) / ULAM_ENERGY_SHARE),
        float(Decimal(str(high)) / ULAM_ENERGY_SHARE),
    )
    for group, (low, high) in FOOD_GROUP_TARGETS.items()
    if group != "go"
}


# ── Staple meals (not judged as an ulam) ───────────────────────────────
# Meals that are themselves the Go-group staple. The ulam-only calorie
# bracket and Grow/Glow bands don't apply to them, so nutritional
# adequacy is reported as "not applicable" (see service.py) rather than
# a false fail. Names are compared lowercased. A name list is a quick
# fix; move to a Meal column if more staples are added.
STAPLE_MEAL_NAMES: frozenset[str] = frozenset({"garlic fried rice"})


def is_staple_meal(meal_name: str) -> bool:
    return meal_name.strip().lower() in STAPLE_MEAL_NAMES


def get_per_meal_bracket(daily_kcal: int) -> tuple[float, float]:
    """
    Returns (lower, upper) kcal bounds for a single ulam/dish.

    Scaled by ULAM_ENERGY_SHARE since seeded Meals represent the ulam
    alone, not a full rice+ulam plate — see the comment block above
    ULAM_ENERGY_SHARE.
    """
    full_meal_target = Decimal(daily_kcal) / MEALS_PER_DAY
    target = full_meal_target * ULAM_ENERGY_SHARE
    lower = target * (Decimal("1") - PER_MEAL_TOLERANCE)
    upper = target * (Decimal("1") + PER_MEAL_TOLERANCE)
    return float(lower), float(upper)


# ── Ingredient -> gram conversion (Week 8, Part 2 open decision) ──────
# Only needed for ingredients classified go/grow/glow (see
# ingredient_food_groups) AND not already stored in g/kg. Ingredients
# classified "other" never enter the proportion calculation, so they
# need no conversion regardless of unit.
#
# Confidence noted per entry: "high" = USDA/produce-industry sourced,
# "medium" = standard culinary conversion norms, "low" = estimate
# based on comparable produce sizes (no precise published figure
# found). Given current meal data is sample/placeholder, precision
# here is proportionate — revisit if/when real recipe data replaces it.
INGREDIENT_GRAM_CONVERSIONS: dict[tuple[str, str], float] = {
    ("flour", "cup"): 120,
    ("lumpia wrappers", "pcs"): 10,
    ("egg", "pcs"): 50,
    ("canned sardines", "pcs"): 155,
    ("corned beef", "pcs"): 150,
    ("ampalaya", "pcs"): 150,
    ("bell pepper", "pcs"): 120,
    ("cabbage", "cup"): 90,
    ("carrot", "pcs"): 61,
    ("carrots", "pcs"): 61,
    ("cauliflower", "cup"): 100,
    ("eggplant", "pcs"): 80,
    ("kangkong", "cup"): 70,
    ("okra", "pcs"): 12,
    ("chili leaves", "cup"): 70,
    ("green papaya", "pcs"): 500,
    ("onion", "pcs"): 110,
    ("bean sprouts", "cup"): 104,
    # Added after scripts/debug_food_group_exclusions.py. USDA reference
    # weights for one piece: medium tomato 123 g; medium potato
    # (2-1/4" to 3-1/4" dia) 213 g; sweet potato 5" long 130 g; oriental
    # radish / daikon (labanos) 7" long 338 g; quail egg 9 g.
    ("tomato", "pcs"): 123,
    ("potato", "pcs"): 213,
    ("sweet potato", "pcs"): 130,
    ("radish", "pcs"): 338,
    ("quail egg", "pcs"): 9,
}


def convert_to_grams(
    ingredient: str,
    unit: str,
    quantity: Decimal,
) -> Decimal | None:
    """
    Converts a (ingredient, unit, quantity) to grams, for food-group
    proportion calculation.

    Returns None if:
    - unit is already g/kg (caller should handle the trivial case
      directly rather than calling this), or
    - no conversion factor is known for this (ingredient, unit) pair.

    A None return means "exclude this ingredient from the proportion
    calculation" (Week 8, Part 5, item 15's documented fallback) —
    it does NOT mean the ingredient is misclassified, just that its
    mass can't currently be estimated.
    """
    unit_key = unit.strip().lower()
    ingredient_key = ingredient.strip().lower()

    if unit_key in ("g", "kg"):
        return quantity if unit_key == "g" else quantity * 1000

    grams_per_unit = INGREDIENT_GRAM_CONVERSIONS.get(
        (ingredient_key, unit_key)
    )
    if grams_per_unit is None:
        return None

    return quantity * Decimal(str(grams_per_unit))