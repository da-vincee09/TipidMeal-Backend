# TipidMeal Backend

Backend API for **TipidMeal**, a mobile application that helps users discover affordable, personalized meals based on their budget, cooking skills, dietary restrictions, ingredient preferences, pantry availability, meal-planning needs, grocery requirements, saved favorites, and nutritional adequacy against Philippine dietary standards.

Built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL (Supabase)**, **Supabase Auth**, and **Alembic**.

> **Project status:** 🚧 In Development — **Week 8 (Nutrition) built and evaluated; ingredients normalized into a shared reference table; results pending final data verification** (see the Known gap under Meals and "Nutrition Methodology & Limitations").

---

## 🚀 Tech Stack

- **FastAPI** – REST API framework
- **SQLAlchemy 2.0** – ORM
- **PostgreSQL (Supabase)** – Database
- **Supabase Auth** – User authentication
- **Supabase Storage** – Profile image storage
- **Pydantic v2** – Data validation
- **JWT / JWKS** – Supabase access-token verification
- **Alembic** – Database migrations
- **python-jose** – JWT verification
- **python-multipart** – Multipart/form-data parsing for image uploads
- **tzdata** – IANA timezone database (required on Windows; see Installation)

---

# 📁 Project Structure

````text
backend/
│
├── app/
│   ├── api/
│   │   └── router.py
│   └── main.py
│
├── core/
│   ├── config.py
│   ├── constants.py
│   ├── database.py
│   ├── dependencies.py
│   └── utils.py
│
├── features/
│   │
│   ├── profiles/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── profile.py
│   │   │   ├── food_allergy.py
│   │   │   └── disliked_ingredient.py
│   │   ├── schemas.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── router.py
│   │
│   ├── ingredients/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── ingredient.py
│   │   │   └── ingredient_price.py
│   │   └── repository.py
│   │
│   ├── pantry/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── pantry_item.py
│   │   ├── schemas.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── router.py
│   │
│   ├── meals/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── meal.py
│   │   │   ├── meal_ingredient.py
│   │   │   └── meal_instruction.py
│   │   ├── schemas.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── router.py
│   │
│   ├── recommendations/
│   │   ├── models/
│   │   │   └── ingredient_substitution.py
│   │   ├── schemas.py
│   │   ├── rules.py
│   │   ├── scoring.py
│   │   ├── tfidf.py
│   │   ├── utils.py
│   │   ├── service.py
│   │   └── router.py
│   │
│   ├── meal_planner/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── meal_plan_entry.py
│   │   ├── schemas.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── router.py
│   │
│   ├── grocery_list/
│   │   ├── schemas.py
│   │   ├── service.py
│   │   └── router.py
│   │
│   ├── favorites/
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── favorite.py
│   │   ├── schemas.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── router.py
│   │
│   └── nutrition/
│       ├── models/
│       │   └── ingredient_food_group.py
│       ├── constants.py
│       ├── schemas.py
│       ├── service.py
│       └── router.py
│
├── scripts/
│   ├── __init__.py
│   ├── evaluate_nutrition_adequacy.py
│   └── debug_food_group_exclusions.py
│
├── shared/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt.py
│   │   └── dependencies.py
│   │
│   ├── database/
│   │   ├── base.py
│   │   └── models.py
│   │
│   ├── storage/
│   │   └── supabase_storage.py
│   │
│   ├── responses/
│   │   └── base_response.py
│   │
│   └── schemas/
│       └── pagination.py
│
├── alembic/
│   └── versions/
│
├── requirements.txt
└── .env
````

---

# 🏗️ Backend Architecture

The backend follows a feature-based layered architecture.

For features that require database persistence:

````text
Router
   ↓
Service
   ↓
Repository
   ↓
SQLAlchemy Models
   ↓
PostgreSQL
````

The Grocery List feature is different because it is a **computed feature**.

Instead of storing grocery-list records in a new database table, the grocery list is generated from existing application data:

````text
Router
   ↓
Grocery List Service
   ↓
Meal Planner + Meals + Pantry + Ingredient Prices
   ↓
Computed Grocery List (with pricing, where known)
````

Favorites follows the standard persisted-feature pattern, structurally similar to Meal Planner — a join table between a user's profile and a meal, scoped by ownership:

````text
Router
   ↓
Favorites Service
   ↓
Favorites Repository
   ↓
Favorite Model
   ↓
PostgreSQL
````

**Ingredients is a shared reference module, not a standard CRUD feature.** It has models and a repository, but no router or service of its own — there is currently no `/ingredients` API endpoint. Other features (Meals, Pantry, Nutrition, Grocery List) query `Ingredient`, `IngredientFoodGroup`, and `IngredientPrice` directly through SQLAlchemy relationships. This is a deliberate architectural exception: ingredients are pure reference data consumed by several features, not something a client creates or lists directly (yet).

Nutrition (Week 8) is also a **computed feature**. Nothing about a meal's adequacy is stored; it is calculated on request from the meal, the caller's profile, and a small static/reference data layer:

````text
Router
   ↓
Nutrition Service
   ↓
Meal + Profile + ingredient_food_groups (via Ingredient FK)
   +
features/nutrition/constants.py (PDRI, PAL, Pinggang Pinoy, conversions)
   ↓
Computed Nutritional Adequacy
````

Each major feature is isolated inside its own module.

Current backend modules:

````text
Profiles
Ingredients      (reference data only, no router)
Pantry
Meals
Recommendations
Meal Planner
Grocery List
Favorites
Nutrition
````

Shared functionality such as authentication, database configuration, storage, and common schemas is placed inside `shared/`. App-wide constants (e.g. timezone-sensitive cutoffs) live in `core/constants.py`, with small pure helper functions in `core/utils.py`. Nutrition's static reference data lives with the feature in `features/nutrition/constants.py`.

## Ingredient Normalization

Ingredients were originally free-text strings duplicated across `meal_ingredients.ingredient`, `pantry_items.ingredient`, and `ingredient_food_groups.ingredient_name`. They are now normalized into one `ingredients` table (`id`, unique `name`), referenced by foreign key from `meal_ingredients`, `pantry_items`, `ingredient_food_groups`, and the new `ingredient_prices` table.

To avoid touching every downstream call site (Recommendations, Grocery List, Nutrition all previously read `.ingredient` as a plain string), `MealIngredient` and `PantryItem` both expose a read-only `.ingredient` **property** that resolves through the relationship:

````python
@property
def ingredient(self) -> str:
    return self.ingredient_ref.name
````

This preserves the existing string-based contract everywhere else in the codebase while the actual storage is now relational. `ingredient_ref` uses `lazy="joined"` on both models, so reading `.ingredient` doesn't cause an N+1 query pattern.

---

# 🔐 Authentication

Authentication is handled by **Supabase Auth**.

FastAPI verifies Supabase access tokens using Supabase's JWKS endpoint.

The backend currently supports:

* Supabase JWT verification
* JWKS public-key retrieval
* ES256 signature verification
* Authenticated-user dependency
* Protected API routes
* Authentication failure handling
* User identity extraction from the JWT `sub` claim

Authentication flow:

````text
Supabase Auth
      ↓
JWT Access Token
      ↓
FastAPI
      ↓
JWKS Public Key
      ↓
ES256 Verification
      ↓
Authenticated Supabase User UUID
````

The authenticated Supabase UUID is used as the identity source for application-level user data.

Protected requests use:

````text
Authorization: Bearer <Supabase Access Token>
````

---

# 👤 Profile Module

The profile module manages application-specific user information.

Profile fields include:

* Profile Image URL
* First Name
* Last Name
* Date of Birth
* Sex
* Budget Per Meal
* Cooking Skill Level
* Physical Activity Level
* Food Allergies
* Disliked Ingredients

Implemented:

* Profile creation
* Profile retrieval
* Profile updates
* Food allergy relationships
* Disliked ingredient relationships
* Profile image upload
* Supabase Storage integration
* Authenticated-user ownership
* Physical activity level (Week 7 — see below)

Profile architecture:

````text
Authenticated User
       ↓
Profile
       ├── Food Allergies
       └── Disliked Ingredients
````

The profile data is used by the recommendation system to personalize meal recommendations, and (as of Week 8) by the Nutrition module to determine each user's daily caloric requirement.

## Budget Per Meal (renamed, post-Week 7)

The field originally named `daily_budget` was renamed to **`budget_per_meal`** — both the database column and every reference in code (schemas, repository, recommendation scoring, Flutter models/UI). The rename reflects how the value was already actually being used: `calculate_budget_score()` and the Week 7 affordability filter both compare a *single meal's* estimated cost directly against this number, not against a fraction of it — so "daily budget" was a misleading label for what was functionally a per-meal ceiling the whole time. No behavior changed; only the name, everywhere.

Migration: `c7d8e9f0a1b2_rename_daily_budget_to_budget_per_meal.py` — a plain `RENAME COLUMN`, so existing data is preserved.

## Physical Activity Level (Week 7)

A `physical_activity_level` column was added to `Profile` as groundwork for Week 8's Nutrition feature (PDRI-based caloric bracket calculation).

- **Enum:** `sedentary`, `moderately_active`, `active` — a 3-category scheme matching the PDRI's own activity classification.
- **Required on profile creation.** `ProfileCreate.physical_activity_level` has no default and is not `Optional` — every new profile must specify it. This is a deliberate product decision made during implementation.
- The database column itself is nullable (`String(50)`, `nullable=True`) purely so pre-existing profiles created before this migration don't violate a NOT NULL constraint retroactively — but the API enforces it as required for any newly-created profile going forward. `ProfileUpdate` and `ProfileResponse` keep it optional so partial updates and pre-Week-7 rows still round-trip correctly.
- Migration: `aa4a5f458607_add_physical_activity_level_to_profiles.py`.
- **Used by the Nutrition module (Week 8)** to scale the PDRI energy requirement for activity level (see Nutrition Module below). It is **not** used in recommendation scoring — the hybrid score is unchanged (Coverage/Budget/Skill/Allergy/Disliked, see Recommendation Scoring below).

---

# 🧂 Ingredients Module (reference data)

A shared, normalized ingredient vocabulary consumed by Meals, Pantry, Nutrition, and Grocery List. No dedicated API router exists yet — this is queried internally, not exposed as its own CRUD endpoint.

## `ingredients`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Primary key |
| `name` | String(100) | Unique, indexed |

## `ingredient_prices`

Optional per-unit price for an ingredient, feeding Grocery List's cost estimate.

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Primary key |
| `ingredient_id` | UUID | FK → `ingredients.id` |
| `unit` | String(50) | e.g. `g`, `pcs`, `cup` |
| `price_per_unit` | Numeric(10,2) | ₱ per one unit |

Unique on `(ingredient_id, unit)` — an ingredient can have a different price per unit it's sold in (e.g. price per `g` vs. price per `pcs`), but not two prices for the same unit.

> ⚠️ **Seed status unconfirmed.** Whether `ingredient_prices` has been populated with real data isn't something I've verified. If it's empty, Grocery List's pricing feature is present in code but every item will show `estimated_cost: null` until prices are added — functionally identical to before pricing existed. Confirm seed data exists (or add it) before relying on grocery list totals for anything user-facing.

## Ingredient → Food Group linkage (Week 8, updated)

`ingredient_food_groups` originally joined to ingredients by matching a free-text `ingredient_name` string. It's now a proper foreign key to `ingredients.id`:

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Primary key |
| `ingredient_id` | UUID | FK → `ingredients.id`, unique (at most one food-group row per ingredient) |
| `food_group` | String(20) | `go`, `grow`, `glow`, or `other` |

Migration `h6c7d8e9f0a1` performed this conversion: added the new FK column, backfilled it by matching `lower(trim(name))` against the old `ingredient_name` string, **failed loudly** (raised an exception) if any row couldn't be matched rather than silently leaving orphaned rows, then dropped the old `ingredient_name` column entirely. It also added food-group rows for four ingredients that had none (`milk`, `evaporated_milk` → grow; `butter`, `margarine` → other).

---

# 🥫 Pantry Module

The pantry module represents ingredients currently available to an authenticated user.

Example:

````text
Rice        2 kg
Chicken     1 kg
Eggs        6 pcs
Tomato      4 pcs
````

Each pantry item belongs to a user's application profile.

Implemented:

* Pantry item model
* Pydantic schemas
* Repository layer
* Service layer
* API router
* Authenticated-user ownership
* Pantry item creation
* Pantry item retrieval
* Pantry item updates
* Pantry item deletion
* Quantity handling
* Unit handling
* Ingredient quantity aggregation

Pantry architecture:

````text
Authenticated User
       ↓
Profile
       ↓
Pantry Items (ingredient_id → Ingredient)
       ↓
PostgreSQL
````

`PantryItem.ingredient` is now a read-only property resolving `ingredient_id` through the `Ingredient` relationship (see "Ingredient Normalization" above), not a stored string column. Existing update logic for changing a pantry item's ingredient is handled explicitly in `repository.update_pantry_item()` rather than generic `setattr`, since the property itself can't be assigned to directly.

## Pantry Quantity Handling

Pantry availability is represented using:

````text
Ingredient
    ↓
Unit
    ↓
Quantity
````

Example:

````python
{
    "rice": {
        "kg": 2
    },
    "eggs": {
        "pcs": 6
    },
    "tomato": {
        "pcs": 4
    }
}
````

Multiple pantry entries for the same ingredient and unit can be combined.

For example:

````text
Rice
2 kg
+
1 kg
=
3 kg
````

Different units are kept separately.

For example:

````text
Rice
kg → 2
g  → 500
````

The backend does not currently perform automatic unit conversion.

---

# 🍽️ Meals Module

The meals module provides the application's meal database.

A meal contains:

* Name
* Description
* Image URL
* Estimated Cost
* Cooking Time
* Difficulty
* Servings
* Calories

Meals contain related ingredients and cooking instructions.

Relationship:

````text
Meal
 │
 ├── Meal Ingredients (ingredient_id → Ingredient)
 │
 └── Meal Instructions
````

Implemented:

* Meal model
* Meal ingredient model
* Meal instruction model
* Pydantic schemas
* Repository layer
* Service layer
* API router
* Meal retrieval
* Meal detail retrieval
* Ingredient relationships
* Instruction relationships
* Ingredient suggestion search

`Meal.estimated_cost` is stored as `Numeric(10, 2)` (not `Float`), and the Pydantic schemas type it as `Decimal` end-to-end — this avoids floating-point rounding artifacts at the source, rather than only masking them at display time. See "Peso Precision (Week 7)" under the Meal Planner Module below.

`Meal.difficulty` is a free `String(50)` with no enum constraint at the database level. The recommendation engine's skill-scoring table (see Recommendation Scoring below) expects exactly `easy`, `medium`, or `hard` (case-insensitive); any other value would score `0.0` regardless of the user's skill level, since it wouldn't match a key in the compatibility table. All 20 currently seeded meals were checked and confirmed to use exactly one of these three values (Week 7, Day 3).

`Meal.calories` feeds the Nutrition module's caloric-adequacy check (Week 8), where it is compared against a per-meal bracket. It therefore needs to represent calories for **one serving** of the dish.

Like Pantry, `MealIngredient.ingredient` is now a read-only property resolving through `ingredient_id → Ingredient.name`, not a stored string.

> ⚠️ **Known gap (Week 7, Day 4 — not yet done):** `Meal.servings` and the associated ingredient quantities/cost/calories in the current seed data are **sample data** and have not yet been normalized to represent exactly 1 serving. Because the Nutrition caloric check depends on `Meal.calories`, the nutritional-adequacy figures should be treated as provisional until this is done.

---

# 🔎 Ingredient Suggestions

The Meals module provides ingredient autocomplete functionality.

Endpoint:

````text
GET /api/v1/meals/ingredients/suggestions?search=tom
````

The endpoint:

* Accepts a search string
* Performs case-insensitive matching
* Returns distinct ingredient names
* Sorts results alphabetically
* Limits results to 10 suggestions by default

Example response:

````json
[
  "Tomato",
  "Tomato Paste",
  "Tomato Sauce"
]
````

---

# 🤖 Recommendation Module

The recommendation system uses a deterministic, rule-based approach.

No external AI API is required for the current recommendation engine.

The recommendation pipeline is:

````text
Profile
   +
Pantry
   +
Meals
   +
Recommendation Rules
   ↓
Affordability Filter (hard — Week 7)
   ↓
Ingredient Adaptation
   ↓
Scoring
   ↓
Allergy Filter (hard)
   ↓
Ranking / Sort
   ↓
Recommended Meals
````

Recommendations consider:

* Ingredient availability
* Pantry quantities
* Ingredient units
* Ingredient substitutions
* Estimated meal cost
* User's budget per meal
* Cooking skill
* Food allergies
* Disliked ingredients
* Ingredient coverage

**Week 8:** the recommendation response is also extended with each meal's nutritional-adequacy result (see Nutrition Module below), so the Flutter client can show a nutrition badge on recommendation cards. This is informational — the hybrid score weights and the ranking rules below are unchanged.

## Affordability (Week 7 — hard filter)

As of Week 7, any meal whose `estimated_cost` exceeds the user's `budget_per_meal` is excluded from the recommendation list entirely, before ingredient adaptation, coverage, or scoring are calculated. This is a deliberate product decision made during implementation, stricter than the system's original design, in which Budget Compatibility was only a 30%-weighted *scored* factor (see Recommendation Scoring below) rather than a pass/fail gate. The 30% weight still differentiates among the meals that pass this gate — it just no longer decides, on its own, whether an over-budget meal can appear at all.

One practical effect: `calculate_budget_score()`'s two lowest tiers (`ratio 1.00–1.25 → 0.50` and `ratio > 1.25 → 0.00`) can no longer be reached in production, since anything with `ratio > 1.00` is already excluded upstream by this filter.

---

# 📊 Recommendation Scoring

The current hybrid scoring system uses:

| Factor                | Weight |
| --------------------- | -----: |
| Ingredient Coverage   |    30% |
| Budget Compatibility  |    30% |
| Cooking Skill         |    10% |
| Allergy Compatibility |    20% |
| Disliked Ingredients  |    10% |

This weighting applies only to meals that already pass the Week 7 affordability hard filter above — Budget Compatibility's 30% now differentiates *among* affordable meals rather than being the sole signal keeping over-budget meals out.

Allergy conflicts are treated as hard restrictions.

A meal containing an allergy conflict receives:

````text
score = 0
````

and is excluded from the response entirely.

The recommendation system is deterministic and explainable, which is useful for evaluation and thesis defense.

## Cost-Based Sort (Week 7)

`GET /api/v1/recommendations` accepts an optional `sort_by` query parameter:

````text
GET /api/v1/recommendations?sort_by=score   (default)
GET /api/v1/recommendations?sort_by=cost
````

- **`sort_by=score`** (default): meals are tiered by pantry-adaptation decision (`adapt` before `fallback`), then ordered by hybrid score descending within each tier.
- **`sort_by=cost`**: meals are ordered by `estimated_cost` ascending, with hybrid score descending as a tiebreaker. Pantry-adaptation tiering is not applied in this mode.
- In both modes, the affordability and allergy hard filters above are applied identically first — `sort_by` only changes ordering among meals that already qualify.
- Verification method: manual testing through the app and Swagger against the 20 seeded meals, not an automated test suite — no unit tests currently exist for `scoring.py`.

## Cooking Skill Scoring (verified, Week 7)

Skill compatibility uses a fixed table, not a linear formula:

| User Skill \ Meal Difficulty | Easy | Medium | Hard |
|---|---|---|---|
| Beginner | 1.00 | 0.60 | 0.20 |
| Intermediate | 1.00 | 1.00 | 0.60 |
| Advanced | 1.00 | 1.00 | 1.00 |

This was manually verified against all 20 seeded meals to confirm:
- A skill mismatch degrades the score smoothly rather than zeroing it out.
- Beginner+Hard (0.20) scores lower than Beginner+Medium (0.60), which scores lower than Beginner+Easy (1.00) — the gap is proportionate to how far apart the levels are, not just "match vs. no match."
- An Advanced-skill user is never penalized for any difficulty, including Easy meals.
- Skill mismatch only reduces score when the meal is *harder* than the user's skill — never when it's easier.

All 20 seeded `Meal.difficulty` values were confirmed to be exactly `easy`, `medium`, or `hard` (case-insensitive), so no meal silently falls outside this table.

---

# 🧩 Ingredient Adaptation

The recommendation system can adapt meal ingredients based on pantry availability and substitution rules.

An ingredient can be classified as:

````text
retain
substitute
insufficient
omit
unavailable
````

Meals are classified as either:

````text
adapt
fallback
````

**Week 7 change:** `fallback` meals are no longer excluded from the recommendation response. They are still returned to the client, just tiered *after* `adapt` meals under the default `sort_by=score` ordering (see Cost-Based Sort above). This differs from the feature's original design.

## Retain

An ingredient is retained when the ingredient exists in the pantry.

If the pantry and recipe units match, the backend compares quantities.

Example:

````text
Required:
Rice → 500 g

Pantry:
Rice → 1 kg

Result:
retain
````

---

## Insufficient

An ingredient is classified as insufficient when:

* The ingredient exists in the pantry.
* The units match.
* The pantry quantity is lower than the required quantity.

Example:

````text
Required:
Rice → 1 kg

Pantry:
Rice → 500 g

Result:
insufficient
````

Example response:

````json
{
  "ingredient": "Rice",
  "action": "insufficient",
  "available_quantity": 500,
  "required_quantity": 1000,
  "unit": "g"
}
````

An insufficient ingredient is treated as a soft warning rather than automatically making the meal a fallback candidate.

---

## Different Units

The backend does not currently perform automatic unit conversion.

Example:

````text
Pantry:
Rice → 1 kg

Recipe:
Rice → 500 g
````

Because the units differ, the backend does not attempt to perform an unsafe quantity comparison.

The ingredient can still be considered present.

---

## Unavailable

An ingredient is classified as unavailable when:

* It is not present in the pantry.
* No valid substitution is available.

Unavailable required ingredients can cause a meal to become a `fallback` candidate — which, as of Week 7, is still returned to the client rather than filtered out (see above).

---

# 🔄 Ingredient Substitutions

Ingredient substitution rules are stored in the database.

Example:

````text
milk
  ↓
evaporated_milk

butter
  ↓
margarine
````

The substitution system allows the recommendation engine to determine whether an unavailable ingredient can be replaced with another available ingredient.

The database contains an:

````text
ingredient_substitutions
````

table.

> Note: this table still stores ingredient names as free text (`ingredient`, `substitute` columns) — it was not part of the ingredients-normalization refactor. It's a separate, independent table from `ingredients`/`ingredient_food_groups`/`ingredient_prices`.

---

# 🧠 TF-IDF Ingredient Coverage

The recommendation system includes a TF-IDF-based ingredient weighting component.

Instead of treating all ingredients as equally important, TF-IDF can estimate the relative importance of ingredients within the meal corpus.

The recommendation system combines ingredient coverage with the other deterministic scoring factors.

Quantity sufficiency is handled separately from name-based ingredient coverage.

---

# 📅 Meal Planner Module

The Meal Planner allows authenticated users to schedule meals for specific dates.

Each meal plan entry connects:

````text
Profile
   ↓
Meal Plan Entry
   ↓
Meal
````

A meal plan entry contains:

* Meal
* Planned Date
* Meal Slot
* Creation timestamp
* Update timestamp

Example:

````text
August 18, 2026

Breakfast
    ↓
Oatmeal

Lunch
    ↓
Chicken Adobo

Dinner
    ↓
Vegetable Stir Fry
````

The database model is:

````text
meal_plan_entries
````

with relationships to:

````text
profiles
meals
````

The profile relationship uses cascading deletion, while meal deletion is restricted when referenced by a meal-plan entry.

Implemented:

* Meal plan entry model
* Pydantic schemas
* Repository layer
* Service layer
* API router
* Create meal plan entry
* Retrieve meal plan entries
* Retrieve individual meal plan entries
* Update meal plan entries
* Delete meal plan entries
* Authenticated-user ownership
* Date-based meal planning
* Meal-slot support
* Past-date/slot rejection on create and update (see below)

## Past-Date/Slot Guard (Week 7)

A meal plan entry cannot be created or moved into a date/slot that has already passed.

- Any `planned_date` before today (server `TIMEZONE=Asia/Manila`) is rejected.
- For `planned_date == today`, each meal slot has its own cutoff:

  | Slot      | Cutoff   |
  |-----------|----------|
  | Breakfast | 10:00 AM |
  | Lunch     | 2:00 PM  |
  | Dinner    | 9:00 PM  |

- Cutoff constants live in `core/constants.py`; the check itself is `core/utils.is_planned_slot_in_past()`, called from `service.create_meal_plan_entry()` and `service.update_meal_plan_entry()`.
- Editing an already-past entry without changing its date/slot is still allowed — only a move *into* a past date/slot is rejected.
- Rejected requests return `400` with `{"detail": "Cannot add a meal to a slot that has already passed"}`.

## Peso Precision (Week 7)

`estimated_cost_total` in the weekly Meal Planner response is explicitly quantized to 2 decimal places server-side (`Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`) before serialization, preventing raw floating-point rounding artifacts (e.g. `45.500000000000004`) from reaching the client. Individual `Meal.estimated_cost` values are already stored as `Numeric(10, 2)` end-to-end, so no artifacts are possible there.

---

# 🛒 Grocery List Module

The Grocery List is a **derived feature** that converts a user's meal plan into a list of ingredients that need to be purchased — and, where pricing data is available, estimates what buying them will cost.

The feature connects the Meal Planner, Meals, Pantry, and (as of this update) Ingredient Prices modules.

The overall flow is:

````text
Meal Plan
     ↓
Planned Meals
     ↓
Required Ingredients
     ↓
Combine Duplicate Ingredients
     ↓
Compare Against Pantry
     ↓
Subtract Available Pantry Quantity
     ↓
Remaining Quantity
     ↓
Price Lookup (per ingredient + unit, where known)
     ↓
Grocery List (with estimated cost per item + total)
````

The Grocery List does **not** introduce a new SQLAlchemy model or database table of its own. Instead, the list is computed whenever the endpoint is requested, using `meal_plan_entries`, `meal_ingredients`, `pantry_items`, and — for pricing — `ingredient_prices`.

This keeps the grocery list synchronized with the latest:

* Meal Plan
* Meal Ingredients
* Pantry contents
* Ingredient prices

---

## Grocery List Architecture

Unlike database-backed CRUD features, Grocery List uses a lightweight computed architecture:

````text
Authenticated User
       ↓
Profile
       ↓
Meal Planner
       ↓
Planned Meals
       ↓
Meal Ingredients
       ↓
Grocery List Service ── Ingredient Prices
       ↓
Pantry
       ↓
Computed Grocery List
````

The feature structure is:

````text
features/
└── grocery_list/
    ├── schemas.py
    ├── service.py
    └── router.py
````

No `models/` directory is required for the current computed-only implementation.

---

## Grocery List Calculation

The Grocery List service performs the following operations.

### 1. Retrieve Planned Meals

The service retrieves the authenticated user's planned meals for the requested date range.

Example:

````text
Monday
  Breakfast → Oatmeal
  Lunch     → Chicken Adobo

Tuesday
  Dinner    → Chicken Adobo
````

---

### 2. Retrieve Required Ingredients

The ingredients of all planned meals are collected.

Example:

````text
Oatmeal:
- Oats       100 g
- Milk       200 ml

Chicken Adobo:
- Chicken    500 g
- Soy Sauce  50 ml
- Vinegar    50 ml

Chicken Adobo:
- Chicken    500 g
- Soy Sauce  50 ml
- Vinegar    50 ml
````

---

### 3. Combine Duplicate Ingredients

Ingredients with the same normalized ingredient name and unit are combined.

Example:

````text
Chicken
500 g
+
500 g
=
1000 g
````

Similarly:

````text
Soy Sauce
50 ml
+
50 ml
=
100 ml
````

The Grocery List does not combine ingredients with different units.

Example:

````text
Rice → 1 kg
Rice → 500 g
````

These remain separate because the backend does not currently perform automatic unit conversion.

---

### 4. Compare Against Pantry

The aggregated requirements are compared against the user's current pantry.

Example:

````text
Required:
Rice → 2 kg

Pantry:
Rice → 1 kg
````

The remaining quantity is:

````text
1 kg
````

Therefore:

````text
Grocery List:
Rice → 1 kg
````

---

### 5. Fully Stocked Ingredients

If the pantry already contains enough of an ingredient under the same unit, the ingredient does not need to appear in the grocery list.

Example:

````text
Required:
Eggs → 6 pcs

Pantry:
Eggs → 12 pcs
````

Result:

````text
No eggs need to be purchased.
````

---

### 6. Different Units

The Grocery List follows the same unit-safety rule used by the recommendation system.

Automatic unit conversion is not currently performed.

Example:

````text
Required:
Rice → 500 g

Pantry:
Rice → 1 kg
````

Because the units differ, the backend does not automatically subtract the quantities.

The required amount remains represented in the Grocery List rather than making an unsafe conversion.

---

### 7. Price Lookup (new)

For each item still needing to be bought, the service looks up `(ingredient, unit) → price_per_unit` from `ingredient_prices` via `get_ingredient_price_map()`.

````text
quantity_to_buy x price_per_unit  →  item's estimated_cost
sum of all priced items' estimated_cost  →  total_estimated_cost
````

- Matching is exact on `(ingredient_name, unit)` — the same unit-safety principle as everything else in this module. A price entered for `rice` in `kg` will not be applied to a grocery item that needs `rice` in `g`.
- **If an ingredient has no price entry for its exact unit, `estimated_cost` is `null` for that item** — it is silently omitted from the total rather than guessed or converted.
- `total_estimated_cost` is only populated if **at least one** item in the list had a known price; if nothing could be priced, it's `null` rather than a misleading `₱0.00`.
- **This means the total can understate the true cost of the list** whenever some ingredients are priced and others aren't — there is currently no indicator in the response distinguishing "nothing left to buy" from "some items left to buy have no known price." Worth flagging to the user in the UI (e.g. "partial total — some prices unavailable") if this matters for how the feature is presented.

---

# 🧾 Grocery List Schemas

A Grocery List item contains:

````text
Ingredient
Unit
Required Quantity
Pantry Quantity
Quantity to Buy
Estimated Cost (optional)
````

````json
{
  "ingredient": "Chicken",
  "unit": "g",
  "required_quantity": 1000,
  "pantry_quantity": 500,
  "quantity_to_buy": 500,
  "estimated_cost": 90.00
}
````

An item with no known price for its unit:

````json
{
  "ingredient": "Bay Leaves",
  "unit": "pcs",
  "required_quantity": 3,
  "pantry_quantity": 0,
  "quantity_to_buy": 3,
  "estimated_cost": null
}
````

The overall response also contains the date range covered, and an optional running total:

````json
{
  "start_date": "2026-09-15",
  "end_date": "2026-09-21",
  "items": [ /* ... */ ],
  "total_estimated_cost": 342.50
}
````

`total_estimated_cost` is `null` if no item in the list had a known price.

---

# 📆 Grocery List Date Range

The Grocery List endpoint accepts:

````text
start_date
end_date
````

The date range determines which planned meals contribute ingredients to the grocery list.

If no date range is provided, the backend uses the current week.

Example:

````text
GET /api/v1/grocery-list
````

generates the grocery list for the current week.

A specific date range can also be requested:

````text
GET /api/v1/grocery-list?start_date=2026-08-18&end_date=2026-08-24
````

---

# 🛍️ Grocery List Data Flow

The complete Grocery List flow is:

````text
Supabase Auth
      ↓
Authenticated User
      ↓
Profile
      ↓
Meal Planner
      ↓
Planned Meals
      ↓
Meal Ingredients
      ↓
Ingredient Aggregation
      ↓
Pantry Availability
      ↓
Quantity Comparison
      ↓
Missing Ingredients
      ↓
Price Lookup (ingredient_prices)
      ↓
Grocery List (with pricing where known)
````

This makes the Grocery List the final derived feature of the Pantry + Meals + Meal Planner + Ingredient Prices workflow.

---

# ⭐ Favorites Module

The Favorites module allows authenticated users to bookmark meals from the meal database for quick access later.

Each favorite connects:

````text
Profile
   ↓
Favorite
   ↓
Meal
````

A favorite contains:

* Meal (nested summary: id, name, estimated cost, image URL)
* Creation timestamp

The database model is:

````text
favorites
````

with relationships to:

````text
profiles
meals
````

Unlike Meal Planner, both the profile and meal relationships use cascading deletion — a favorite is a bookmark, not a scheduling record, so it has no reason to outlive either the user or the meal it points to.

A unique constraint on `(profile_id, meal_id)` prevents the same user from favoriting the same meal twice at the database level.

Implemented:

* Favorite model
* Unique constraint on profile + meal
* `meal` relationship (`lazy="joined"`) for eager-loaded meal summaries in responses
* Pydantic schemas
* Repository layer
* Service layer
* API router
* Add favorite
* Retrieve favorites
* Remove favorite
* Authenticated-user ownership
* Idempotent add (favoriting an already-favorited meal returns the existing record instead of raising a conflict)
* Idempotent remove (un-favoriting a meal that isn't favorited is a no-op instead of a 404)

## Favorites Idempotency

Both the add and remove operations are intentionally idempotent, so the Flutter client's optimistic-UI favorite toggle never has to special-case a race condition or a double-tap.

Add:

````text
POST /favorites (meal_id: X)
      ↓
Already favorited?
      ├── Yes → return existing favorite
      └── No  → create new favorite
````

Remove:

````text
DELETE /favorites/{meal_id}
      ↓
Currently favorited?
      ├── Yes → delete favorite
      └── No  → no-op, return 204 anyway
````

Favorites architecture:

````text
Authenticated User
       ↓
Profile
       ↓
Favorites
       ↓
PostgreSQL
````

---

# 🥗 Nutrition Module (Week 8)

The Nutrition module answers one question for a given user and meal: **is this meal nutritionally adequate for this user?** It supports the thesis's Objective 4 (assessing the nutritional adequacy of recommended meals).

A meal is nutritionally adequate only when **both** checks pass:

````text
Caloric adequacy   — the meal's calories fall inside the user's per-meal bracket
        +
Food-group adequacy — the meal's Grow/Glow balance falls inside the Pinggang Pinoy bands
        ↓
Nutritional adequacy
````

Like the Grocery List, Nutrition is a **computed feature**: results are calculated on request and are not persisted. The one table it adds, `ingredient_food_groups`, is reference data, not user data — and, as of this update, it links to `ingredients` by foreign key rather than by name string (see the Ingredients Module above).

Nutrition flow:

````text
Authenticated User
       ↓
Profile (date of birth, sex, physical activity level)
       ↓
Daily Caloric Requirement (PDRI x activity scaling)
       ↓
Per-Meal Caloric Bracket (ulam-scaled, ±20%)
       +
Meal
       ├── Calories → Caloric Adequacy
       └── Ingredients (via Ingredient FK) → grams → Go/Grow/Glow proportions → Food-Group Adequacy
       ↓
Nutritional Adequacy
````

## Standards Used

Two external standards are combined. That combination is a methodological choice, not a single official table, and must be documented as such in the thesis methodology chapter with both sources cited separately:

1. **PDRI 2015 (Revised September 2018), FNRI-DOST** — Recommended Energy Intake by sex and age bracket. PDRI gives one value per sex/age and does not stratify by physical activity.
2. **FAO/WHO/UNU (2001), *Human Energy Requirements*, Table 5.3** — Physical Activity Level (PAL) categories, used as ratios to scale the PDRI value for activity level, anchored on `moderately_active` = the PDRI value as-is.

Food-group targets come from **FNRI-DOST Pinggang Pinoy (2016)**.

## Daily Caloric Requirement

`get_daily_caloric_requirement(date_of_birth, sex, physical_activity_level)` returns the profile's daily kcal need:

````text
daily_kcal = round(PDRI value for (sex, age bracket) x activity scale factor)
````

PDRI baseline (kcal/day, at `moderately_active`):

| Sex    | 19–29 | 30–49 | 50–59 | 60–69 | 70+  |
|--------|------:|------:|------:|------:|-----:|
| Male   | 2530  | 2420  | 2420  | 2140  | 1960 |
| Female | 1930  | 1870  | 1870  | 1610  | 1540 |

Activity scale factors (PAL midpoint ÷ 1.85):

| Activity level      | PAL midpoint | Scale factor |
|---------------------|-------------:|-------------:|
| `sedentary`         | 1.55         | ≈ 0.838      |
| `moderately_active` | 1.85         | 1.000        |
| `active`            | 2.20         | ≈ 1.189      |

Handling of edge cases (each returns an explicit result status rather than raising or silently defaulting):

- **Activity level not set** → `activity_not_set`.
- **Sex other than male/female** (e.g. "Prefer not to say") → `sex_not_supported`, because the PDRI table only has male/female columns.
- **Age below 19** → clamped to the 19–29 bracket as a documented fallback (no adult PDRI bracket exists below 19). Flag for adviser review if pediatric handling matters later.

## Per-Meal Caloric Adequacy

````text
full-meal target = daily_kcal / 3                  (MEALS_PER_DAY = 3)
ulam target      = full-meal target x 0.67          (ULAM_ENERGY_SHARE)
bracket          = ulam target x (1 ± 0.20)         (PER_MEAL_TOLERANCE = ±20%)
````

`meal.calories` is then classified as `below`, `within`, or `above` the bracket, or `unavailable` (see Unavailable States). Example: a male aged 19–29, moderately active (2530 kcal/day) has a bracket of about **452–678 kcal** per dish.

## Ulam-Only Scaling (methodology choice)

Seeded meals are **ulam/viand dishes**; rice and other Go-group staples are modeled as their own separate meals (e.g. Garlic Fried Rice). Both the calorie target and the Pinggang Pinoy bands describe a *whole plate* (staple + ulam), so applying them directly to a single dish would compare an ulam against a plate-sized target. Three app-specific reconciliations address this:

- **`ULAM_ENERGY_SHARE` = 1 − midpoint of the Go band (23–43% → 33%) = 0.67.** The ulam is expected to carry the non-Go share of a meal's energy; the caloric bracket is scaled by it.
- **`ULAM_FOOD_GROUP_TARGETS`.** Go is excluded from the food-group check, and the Grow and Glow bands are divided by the same 0.67, judged as shares of the Grow+Glow total.
- **`STAPLE_MEAL_NAMES`** (currently Garlic Fried Rice). Staples are not judged as an ulam: they report `is_staple: true`, `caloric_adequacy: "unavailable"`, and no adequacy verdict, instead of a false fail.

These are **not official PDRI or Pinggang Pinoy figures** and must be presented as the app's own reconciliation in the methodology chapter.

## Food-Group Adequacy

Each meal's ingredients are classified into Pinggang Pinoy groups and weighed:

1. **Classification.** Each `meal_ingredients` row is resolved to its `Ingredient`, then joined against `ingredient_food_groups` by `ingredient_id` to get `go`, `grow`, `glow`, or `other`. `other` (condiments, seasonings, fats, liquids, sauces) never enters the calculation.
   - The name→group lookup used to key off a lowercased ingredient-name string (`ingredient_food_groups.ingredient_name`); it now goes through the `Ingredient` foreign key. `get_ingredient_food_group_map()` still exposes a `name → group` dict to the rest of `nutrition/service.py` (an ORM join against `Ingredient.name` builds it), so `compute_food_group_proportions()` itself is unchanged.
   - **This map is now cached at the module/process level** (`_food_group_map_cache`), not re-queried on every call as before. It's built once on first use and reused for the life of the running process; a `refresh=True` parameter exists to force a rebuild if needed (e.g. after seeding new ingredients without restarting the server). Worth knowing if you add a new `ingredient_food_groups` row and don't see it reflected without a restart or explicit refresh.
2. **Mass.** Ingredients stored in `g`/`kg` are used directly. Piece- or cup-based ingredients are converted with `INGREDIENT_GRAM_CONVERSIONS` in `features/nutrition/constants.py` (reference weights from USDA and standard culinary conversions, e.g. medium tomato 123 g, medium potato 213 g, 5" sweet potato 130 g, 7" daikon/labanos 338 g, quail egg 9 g).
3. **Proportions.** Grams are summed per group and reported as percentages of the classified total: `{"go": %, "grow": %, "glow": %}`. An ingredient with no classification, or with no gram conversion for its unit, is **excluded from that meal's proportions** rather than guessed.
4. **Verdict (ulam-only).** Go is ignored; Grow and Glow are renormalized to shares of the Grow+Glow total and checked against the ulam bands:

   | Group | Plate-level band (Pinggang Pinoy) | Ulam-only band (÷ 0.67) |
   |-------|-----------------------------------|--------------------------|
   | Go    | 23–43%                            | not scored               |
   | Grow  | 7–27%                             | ≈ 10.4–40.3%             |
   | Glow  | 40–60%                            | ≈ 59.7–89.6%             |

   Because the two shares sum to 100%, the Grow and Glow bands mirror each other. Boundaries are inclusive.

`food_group_proportions` returns the meal's raw three-group split (including Go) for display; the verdict is derived from the ulam-only shares.

## Unavailable States

Adequacy is `None`/`unavailable` — never a silent `false` — when the computation can't be made:

- Physical activity level not set, or a sex value with no PDRI row (caloric side).
- The meal has no `calories` value.
- The meal has no classifiable, measurable ingredients (`food_group_proportions` is `null`), or has no Grow/Glow content to assess.
- The meal is a staple (`is_staple: true`).

`nutritionally_adequate` is `null` whenever either half is unavailable.

## Endpoint and Response

````text
GET /api/v1/meals/{meal_id}/nutrition-adequacy
````

Requires authentication; the result is computed for the authenticated user's own profile. Returns `404` if the meal or the profile does not exist.

Example response:

````json
{
  "caloric_adequacy": "within",
  "food_group_proportions": { "go": 0.0, "grow": 34.6, "glow": 65.4 },
  "food_group_adequate": true,
  "nutritionally_adequate": true,
  "is_staple": false
}
````

| Field | Type | Meaning |
|-------|------|---------|
| `caloric_adequacy` | `within` \| `below` \| `above` \| `unavailable` | Meal calories vs. the per-meal bracket |
| `food_group_proportions` | object \| null | Raw Go/Grow/Glow percentages by mass |
| `food_group_adequate` | bool \| null | Ulam-only Grow/Glow verdict |
| `nutritionally_adequate` | bool \| null | `within` **and** food groups adequate; `null` if either half is unavailable |
| `is_staple` | bool | Staple meal, not judged as an ulam (defaults to `false`) |

## Ingredient Food Groups (reference table)

See the Ingredients Module section above for the current, FK-based schema of `ingredient_food_groups`. It is created and seeded by migration `b1c2d3e4f5a6`, extended by `c2d3e4f5a6b7`, and converted from name-based to FK-based by `h6c7d8e9f0a1`. All ingredients used by the 20 seeded meals are classified. **When adding a meal or ingredient, add a matching row (new migration) — an unclassified ingredient is silently dropped from that meal's proportions.** `scripts/debug_food_group_exclusions.py` lists every dropped ingredient.

Nutrition architecture:

````text
Authenticated User
       ↓
Profile ── Meal
       ↓
Nutrition Service
       ↓
constants.py + ingredient_food_groups (via Ingredient FK)
       ↓
Computed Adequacy (nothing persisted)
````

---

# 📡 API Endpoints

All API routes are versioned under:

````text
/api/v1
````

---

## Profiles

| Method | Endpoint                    | Description                           |
| ------ | ---------------------------- | -------------------------------------- |
| POST   | `/api/v1/profiles`          | Create authenticated user's profile (requires `physical_activity_level`) |
| GET    | `/api/v1/profiles/me`       | Retrieve authenticated user's profile |
| PUT    | `/api/v1/profiles/me`       | Update authenticated user's profile   |
| POST   | `/api/v1/profiles/me/image` | Upload/replace profile picture        |

---

## Pantry

| Method | Endpoint              | Description                          |
| ------ | ---------------------- | ------------------------------------- |
| POST   | `/api/v1/pantry`      | Add pantry item                      |
| GET    | `/api/v1/pantry`      | Retrieve authenticated user's pantry |
| GET    | `/api/v1/pantry/{id}` | Retrieve pantry item                 |
| PUT    | `/api/v1/pantry/{id}` | Update pantry item                   |
| DELETE | `/api/v1/pantry/{id}` | Delete pantry item                   |

---

## Meals

| Method | Endpoint                                | Description                   |
| ------ | ---------------------------------------- | ------------------------------ |
| GET    | `/api/v1/meals`                         | Retrieve available meals      |
| GET    | `/api/v1/meals/ingredients/suggestions` | Search ingredient suggestions |
| GET    | `/api/v1/meals/{meal_id}`               | Retrieve meal details         |

---

## Nutrition

| Method | Endpoint                                     | Description                                                  |
| ------ | ---------------------------------------------- | -------------------------------------------------------------- |
| GET    | `/api/v1/meals/{meal_id}/nutrition-adequacy` | Nutritional adequacy of a meal for the authenticated user's profile |

The Nutrition endpoint is protected using the authenticated Supabase user.

---

## Recommendations

| Method | Endpoint                                | Description                                |
| ------ | ----------------------------------------- | -------------------------------------------- |
| GET    | `/api/v1/recommendations`               | Generate personalized meal recommendations (default `sort_by=score`; includes each meal's nutrition result) |
| GET    | `/api/v1/recommendations?sort_by=cost`  | Same, ordered by estimated cost ascending  |

---

## Meal Planner

| Method | Endpoint                    | Description                |
| ------ | ---------------------------- | ---------------------------- |
| POST   | `/api/v1/meal-planner`      | Create a meal plan entry (rejects past date/slot) |
| GET    | `/api/v1/meal-planner`      | Retrieve meal plan entries |
| GET    | `/api/v1/meal-planner/{id}` | Retrieve a meal plan entry |
| PUT    | `/api/v1/meal-planner/{id}` | Update a meal plan entry (rejects a move into a past date/slot) |
| DELETE | `/api/v1/meal-planner/{id}` | Delete a meal plan entry   |

Meal Planner routes are protected using the authenticated Supabase user.

---

## Grocery List

| Method | Endpoint                                     | Description                                     |
| ------ | ---------------------------------------------- | -------------------------------------------------- |
| GET    | `/api/v1/grocery-list`                       | Generate grocery list for the current week, with per-item and total estimated cost where prices are known |
| GET    | `/api/v1/grocery-list?start_date=&end_date=` | Generate grocery list for a specific date range |

The Grocery List endpoint is protected using the authenticated Supabase user.

The list is calculated dynamically from:

````text
Meal Plan
+
Meal Ingredients
+
Pantry
+
Ingredient Prices
````

No grocery-list records are persisted in the database in the current implementation.

---

## Favorites

| Method | Endpoint                    | Description                     |
| ------ | ----------------------------- | ---------------------------------- |
| POST   | `/api/v1/favorites`         | Add a meal to favorites (idempotent) |
| GET    | `/api/v1/favorites`         | Retrieve authenticated user's favorites |
| DELETE | `/api/v1/favorites/{meal_id}` | Remove a meal from favorites (idempotent) |

Favorites routes are protected using the authenticated Supabase user.

Note the delete endpoint is keyed by `meal_id`, not the favorite's own `id` — the client always knows which meal it's toggling, not the underlying favorite record's identifier.

---

# 🔒 Authorization and User Isolation

Protected endpoints use:

````text
Authorization: Bearer <Supabase Access Token>
````

The authentication flow is:

````text
JWT
 ↓
get_current_user()
 ↓
Supabase auth_id
 ↓
Profile
 ↓
User-owned resources
````

User-specific resources are always scoped to the authenticated user's profile.

For example:

````text
Authenticated User
       ↓
Profile
       ├── Pantry Items
       ├── Meal Plan Entries
       └── Favorites
````

The Grocery List also follows this ownership model.

The authenticated user can only generate a Grocery List using:

````text
Their Meal Plan
+
Their Pantry
````

A user cannot use another user's profile identifier to retrieve another user's grocery requirements, meal plan, or favorites.

The Nutrition endpoint always uses the authenticated user's own profile (date of birth, sex, activity level); there is no way to request adequacy for another user's profile.

`ingredients`, `ingredient_food_groups`, and `ingredient_prices` are all shared reference data, not user-owned — every user reads the same ingredient vocabulary, classifications, and prices.

---

# 🛒 Grocery List and Pantry Relationship

The Grocery List does not duplicate pantry data.

Instead, it reads the latest pantry state when the endpoint is requested.

Therefore:

````text
Add Pantry Item
      ↓
Grocery List recalculates
````

and:

````text
Delete Pantry Item
      ↓
Grocery List recalculates
````

Similarly:

````text
Change Meal Plan
      ↓
Grocery List recalculates
````

This allows the Grocery List to remain a live derived view. The same is true of pricing: if `ingredient_prices` changes, the next grocery-list request reflects it immediately, since nothing about pricing is cached or stored.

---

# 🖼️ Profile Images

Profile images are stored using **Supabase Storage**.

Bucket:

````text
profile-images
````

Supported formats:

* JPEG
* PNG
* WebP

Maximum file size:

````text
5 MB
````

Upload flow:

````text
Client
   ↓
POST /profiles/me/image
   ↓
FastAPI
   ↓
Supabase Storage
   ↓
Public Image URL
   ↓
Profile.profile_image_url
````

The Supabase service-role key is used only on the backend.

It must never be exposed to the client application.

---

# 🗄️ Database

Database provider:

**Supabase PostgreSQL**

Current application tables include:

````text
profiles
   │
   ├── food_allergies
   ├── disliked_ingredients
   └── pantry_items (ingredient_id → ingredients)

ingredients
   │
   ├── ingredient_food_groups (ingredient_id, unique)
   └── ingredient_prices (ingredient_id + unit, unique together)

meals
   │
   ├── meal_ingredients (ingredient_id → ingredients)
   └── meal_instructions

ingredient_substitutions   (still name-based, not part of this refactor)

meal_plan_entries

favorites
````

There is currently **no `grocery_list_items` table**, and nutrition results are not stored — both are computed dynamically from existing data. `ingredient_food_groups` and `ingredient_prices` are both reference tables keyed off `ingredients.id`, with no other foreign keys pointing at them.

Main relationships:

````text
Profile
 ├── Pantry Items ──→ Ingredient
 ├── Food Allergies
 ├── Disliked Ingredients
 ├── Meal Plan Entries
 └── Favorites

Ingredient
 ├── Food Group Entry (0 or 1)
 └── Prices (0 or more, one per unit)

Meal
 ├── Meal Ingredients ──→ Ingredient
 ├── Meal Instructions
 ├── Meal Plan Entries
 └── Favorites
````

Derived Grocery List:

````text
Meal Plan Entries
        +
Meal Ingredients
        +
Pantry Items
        +
Ingredient Prices
        ↓
Computed Grocery List
````

Derived Nutritional Adequacy:

````text
Profile
   +
Meal (calories, ingredients → Ingredient)
   +
ingredient_food_groups
        ↓
Computed Nutritional Adequacy
````

Foreign keys and cascading behavior are defined at the database level where appropriate. `ingredient_food_groups.ingredient_id` cascades on delete from `ingredients` — deleting an ingredient removes its food-group classification automatically.

Meal Plan Entries restrict meal deletion (a meal cannot be deleted while still scheduled), while Favorites cascade on meal deletion (a bookmark to a deleted meal is meaningless and is removed automatically).

---

# 🔄 Recommendation Data Flow

````text
Supabase Auth
      ↓
Authenticated User
      ↓
Profile
      │
      ├── Budget Per Meal
      ├── Cooking Skill
      ├── Allergies
      └── Disliked Ingredients
      │
      ↓
Pantry (ingredient_id → Ingredient)
      │
      ├── Ingredients
      ├── Quantities
      └── Units
      │
      ↓
Meals (ingredient_id → Ingredient)
      │
      ├── Ingredients
      ├── Cost
      └── Difficulty
      │
      ↓
Affordability Filter (hard, Week 7)
      ↓
Ingredient Adaptation
      │
      ├── Retain
      ├── Substitute
      ├── Insufficient
      ├── Omit
      └── Unavailable
      │
      ↓
Ingredient Coverage
      ↓
Budget Score
      ↓
Skill Score
      ↓
Allergy Filtering (hard)
      ↓
Disliked Ingredient Score
      ↓
Hybrid Score
      ↓
Ranking / Sort (score or cost — Week 7)
      ↓
Recommended Meals (+ nutrition result, Week 8)
````

---

# 📅 Meal Planning Data Flow

````text
Supabase Auth
      ↓
Authenticated User
      ↓
Profile
      ↓
Meal Planner
      ↓
Meal Plan Entry
      │
      ├── Planned Date
      ├── Meal Slot
      └── Meal
             ↓
          PostgreSQL
````

Meal-plan entries are scoped to the authenticated user's profile.

---

# 🛒 Grocery List Data Flow

The Grocery List completes the meal-planning workflow.

````text
Meal Planner
      ↓
Planned Meals
      ↓
Required Ingredients
      ↓
Aggregate Ingredients
      ↓
Compare With Pantry
      ↓
Subtract Available Quantities
      ↓
Missing Ingredients
      ↓
Price Lookup
      ↓
Grocery List (with pricing where known)
````

The overall TipidMeal planning workflow is therefore:

````text
Recommendations
      ↓
Meal Selection
      ↓
Meal Planner
      ↓
Grocery List
      ↓
Pantry
````

The Grocery List acts as the bridge between planned meals and shopping requirements.

---

# ⭐ Favorites Data Flow

````text
Supabase Auth
      ↓
Authenticated User
      ↓
Profile
      ↓
Favorites
      ↓
Favorite Entry
      │
      └── Meal
             ↓
          PostgreSQL
````

Favorites are scoped to the authenticated user's profile, and provide a lightweight, independent bookmarking path alongside the main Discover → Plan → Shop workflow — a user can favorite a meal without it being scheduled anywhere in their Meal Planner.

---

# 🥗 Nutrition Data Flow (Week 8)

````text
Supabase Auth
      ↓
Authenticated User
      ↓
Profile ─────────────── Meal
  │                       │
  │ DOB, sex, activity    ├── calories
  ↓                       └── ingredients → Ingredient
PDRI x PAL scaling              │
  ↓                              ↓
Daily kcal                 ingredient_food_groups (via Ingredient FK) + gram conversions
  ↓                              ↓
Per-meal ulam bracket      Go / Grow / Glow proportions
  ↓                              ↓
Caloric adequacy           Food-group adequacy (ulam-only)
  └──────────┬───────────────────┘
             ↓
   Nutritional adequacy (both must pass)
````

---

# 🧪 Backend Testing and Validation

Backend modules can be independently imported and validated before integration testing.

Example Meal Planner validation:

````bash
python -c "from features.meal_planner.models import MealPlanEntry; print(MealPlanEntry.__tablename__)"
````

````bash
python -c "from features.meal_planner.schemas import MealPlanEntryCreate, MealPlanEntryUpdate, MealPlanEntryResponse, WeeklyPlanResponse; print('Meal planner schemas OK')"
````

````bash
python -c "from features.meal_planner.repository import create_meal_plan_entry, get_meal_plan_entries, get_meal_plan_entry_by_id, update_meal_plan_entry, delete_meal_plan_entry; print('Meal planner repository OK')"
````

````bash
python -c "from features.meal_planner.service import create_meal_plan_entry, get_meal_plan_entries, get_meal_plan_entry_by_id, update_meal_plan_entry, delete_meal_plan_entry; print('Meal planner service OK')"
````

````bash
python -c "from features.meal_planner.router import router; print('Meal planner router OK')"
````

````bash
python -c "from core.utils import is_planned_slot_in_past, get_app_now; print('Core utils OK')"
````

Ingredients validation (new):

````bash
python -c "from features.ingredients.models.ingredient import Ingredient; print(Ingredient.__tablename__)"
````

````bash
python -c "from features.ingredients.models.ingredient_price import IngredientPrice; print(IngredientPrice.__tablename__)"
````

Grocery List validation:

````bash
python -c "from features.grocery_list.schemas import GroceryListItem, GroceryListResponse; print('Grocery list schemas OK')"
````

````bash
python -c "from features.grocery_list.service import get_grocery_list, get_ingredient_price_map; print('Grocery list service OK')"
````

````bash
python -c "from features.grocery_list.router import router; print('Grocery list router OK')"
````

Favorites validation:

````bash
python -c "from features.favorites.models import Favorite; print(Favorite.__tablename__)"
````

````bash
python -c "from features.favorites.schemas import FavoriteCreate, FavoriteResponse; print('Favorites schemas OK')"
````

````bash
python -c "from features.favorites.repository import create_favorite, get_favorite_by_profile_and_meal, get_favorites_by_profile, delete_favorite; print('Favorites repository OK')"
````

````bash
python -c "from features.favorites.service import create_favorite, get_favorites_by_profile, delete_favorite; print('Favorites service OK')"
````

````bash
python -c "from features.favorites.router import router; print('Favorites router OK')"
````

Recommendations validation:

````bash
python -c "from features.recommendations.service import calculate_meal_coverage; print('Recommendations service OK')"
````

````bash
python -c "from features.recommendations.scoring import calculate_budget_score, calculate_skill_score, calculate_allergy_score, calculate_disliked_ingredient_score, calculate_hybrid_score; print('Recommendations scoring OK')"
````

````bash
python -c "from features.recommendations.router import router; print('Recommendations router OK')"
````

Nutrition validation:

````bash
python -c "from features.nutrition.constants import get_daily_caloric_requirement, get_per_meal_bracket, ULAM_FOOD_GROUP_TARGETS, STAPLE_MEAL_NAMES; print('Nutrition constants OK')"
````

````bash
python -c "from features.nutrition.models.ingredient_food_group import IngredientFoodGroup; print(IngredientFoodGroup.__tablename__)"
````

````bash
python -c "from features.nutrition.schemas import NutritionAdequacyResponse; print('Nutrition schemas OK')"
````

````bash
python -c "from features.nutrition.service import compute_nutritional_adequacy, get_ingredient_food_group_map; print('Nutrition service OK')"
````

````bash
python -c "from features.nutrition.router import router; print('Nutrition router OK')"
````

Profiles validation:

````bash
python -c "from features.profiles.models.profile import Profile, CookingSkillLevel, PhysicalActivityLevel; print('Profile model OK')"
````

````bash
python -c "from features.profiles.schemas import ProfileCreate, ProfileUpdate, ProfileResponse; print('Profile schemas OK')"
````

The complete FastAPI application can be verified with:

````bash
python -c "from app.main import app; print('FastAPI app OK')"
````

> **Note:** No automated unit tests currently exist for `scoring.py`, the recommendation pipeline, or the Nutrition module (Weeks 7–8). Skill scoring, cost sort, the affordability filter, and nutritional adequacy have been verified manually through Swagger, hand calculations, and the running app, against the 20 seeded meals, rather than with `pytest`.

---

# 🧪 Grocery List Validation

The Grocery List should be tested against the following scenarios.

### Empty Meal Plan

````text
Meal Plan
    ↓
No planned meals
    ↓
Empty Grocery List
````

The endpoint should return an empty list rather than producing an error.

---

### Fully Stocked Pantry

````text
Required:
Rice → 1 kg

Pantry:
Rice → 1 kg

Result:
Nothing to buy
````

---

### Partially Stocked Pantry

````text
Required:
Rice → 2 kg

Pantry:
Rice → 1 kg

Result:
Rice → 1 kg to buy
````

---

### Duplicate Ingredients

````text
Meal A:
Chicken → 500 g

Meal B:
Chicken → 500 g

Required:
Chicken → 1000 g
````

The duplicate ingredient should be aggregated before pantry subtraction.

---

### Different Units

````text
Required:
Rice → 500 g

Pantry:
Rice → 1 kg
````

The backend should not perform automatic unit conversion.

---

### Priced Item (new)

````text
Rice → 1 kg to buy
Price entry: rice / kg / ₱55.00
      ↓
estimated_cost: 55.00
````

### Unpriced Item (new)

````text
Bay Leaves → 3 pcs to buy
No price entry for (bay leaves, pcs)
      ↓
estimated_cost: null, excluded from total_estimated_cost
````

### Mixed List Total (new)

````text
Item A priced at ₱55.00, Item B unpriced
      ↓
total_estimated_cost: 55.00 (Item B silently excluded — see caveat above)
````

---

### User Isolation

````text
User A
  ↓
Meal Plan A
  +
Pantry A
  ↓
Grocery List A
````

User A must never receive ingredients derived from User B's meal plan or pantry.

---

# 🧪 Favorites Validation

The Favorites module should be tested against the following scenarios.

### Add New Favorite

````text
POST /favorites (meal_id: X)
      ↓
201 Created
      ↓
Favorite returned with nested meal summary
````

---

### Add Duplicate Favorite

````text
POST /favorites (meal_id: X)
      ↓
Already favorited
      ↓
201 Created (same favorite returned, not a 409 conflict)
````

---

### Remove Existing Favorite

````text
DELETE /favorites/{meal_id}
      ↓
204 No Content
      ↓
Favorite no longer appears in GET /favorites
````

---

### Remove Non-Existent Favorite

````text
DELETE /favorites/{meal_id}
      ↓
Not currently favorited
      ↓
204 No Content (no-op, not a 404)
````

---

### User Isolation

````text
User A
  ↓
Favorites A

User B
  ↓
Favorites B
````

User A must never see or be able to delete User B's favorites.

---

# 🧪 Meal Planner Past-Slot Guard Validation (Week 7)

### Yesterday

````text
POST /meal-planner (planned_date: yesterday)
      ↓
400 Bad Request
      ↓
"Cannot add a meal to a slot that has already passed"
````

### Today, Slot Cutoff Already Passed

````text
POST /meal-planner (planned_date: today, meal_slot: breakfast, now > 10:00 AM)
      ↓
400 Bad Request
````

### Today, Slot Still Open / Any Future Date

````text
POST /meal-planner (planned_date: today, meal_slot: dinner, now < 9:00 PM)
      ↓
201 Created
````

### Editing an Already-Past Entry Without Moving It

````text
PUT /meal-planner/{id} (meal_id changed only, planned_date/meal_slot unchanged, already in the past)
      ↓
200 OK — not blocked
````

### Editing an Entry Into the Past

````text
PUT /meal-planner/{id} (planned_date moved to yesterday)
      ↓
400 Bad Request
````

---

# 🧪 Recommendations Validation (Week 7)

### Affordability Hard Filter

````text
Meal cost > profile.budget_per_meal
      ↓
Excluded from response entirely — never scored or returned
````

### Cost Sort

````text
GET /recommendations?sort_by=cost
      ↓
Meals ordered by estimated_cost ascending
      ↓
hybrid_score used only as a tiebreaker
````

### Score Sort (default)

````text
GET /recommendations (or ?sort_by=score)
      ↓
adapt-tier meals first, then fallback-tier
      ↓
hybrid_score descending within each tier
````

### Skill Scoring

````text
Beginner + Hard meal    → 0.20
Beginner + Medium meal  → 0.60
Beginner + Easy meal    → 1.00
Advanced + any meal     → 1.00 (never penalized)
````

Verified manually against all 20 seeded meals via Swagger; no automated test coverage yet.

---

# 🧪 Nutrition Validation (Week 8)

The Nutrition module should be tested against the following scenarios.

### Daily Caloric Requirement

````text
Male, 19-29, moderately_active   → 2530 kcal/day
Female, 30-49, sedentary         → round(1870 x 1.55/1.85) = 1567 kcal/day
Male, 19-29, active              → round(2530 x 2.20/1.85) = 3009 kcal/day
````

### Per-Meal Bracket

````text
Male, 19-29, moderately_active (2530 kcal/day)
      ↓
2530 / 3 = 843.3  →  x 0.67 = 565.0
      ↓
Bracket: 452.0 - 678.0 kcal
````

### Caloric Adequacy

````text
meal.calories < 452   → "below"
452 <= calories <= 678 → "within"
meal.calories > 678   → "above"
````

### Food-Group Adequacy (ulam-only)

````text
Sinigang na Baboy   500 g grow, 944 g glow  → grow share 34.6%  → adequate
Beef Tapa           500 g grow, 0 g glow    → grow share 100%   → not adequate
````

### Unavailable / Edge Cases

````text
physical_activity_level not set  → caloric_adequacy "unavailable", nutritionally_adequate null
sex not male/female              → caloric_adequacy "unavailable"
age under 19                     → clamped to the 19-29 bracket
Garlic Fried Rice (staple)       → is_staple true, caloric "unavailable", nutritionally_adequate null
meal with no classifiable ingredients → food_group_proportions null, nutritionally_adequate null
````

### Missing Meal or Profile

````text
GET /meals/{unknown_id}/nutrition-adequacy → 404 "Meal not found"
Authenticated user without a profile       → 404 "Profile not found"
````

---

# 📈 Nutrition Evaluation Harness (Objective 4)

`scripts/evaluate_nutrition_adequacy.py` produces the nutritional-adequacy accuracy measure for the thesis results. It calls the real `compute_nutritional_adequacy()` (not a re-implementation), so it tests the production logic.

Test matrix:

````text
5 PDRI age brackets (19-29, 30-49, 50-59, 60-69, 70+)
x 2 sexes (male, female)
x 3 activity levels (sedentary, moderately_active, active)
= 30 profiles

30 profiles x every seeded meal = one test case per (profile, meal)
````

Rules:

- **Accuracy** = cases where `nutritionally_adequate` is `true` ÷ evaluable cases.
- **Evaluable** = `nutritionally_adequate` is not `null`. Staple meals and any structurally unavailable case are excluded from the denominator (reported separately) rather than counted for or against.
- The report also breaks accuracy down by criterion (calories within/below/above; food groups adequate) and per meal, since the food-group verdict does not vary by profile — only the calorie check does.
- Output: a printed summary and `nutrition_evaluation_results.csv` (git-ignored; regenerate as needed).

Run from the backend project root, inside the venv:

````bash
python -m scripts.evaluate_nutrition_adequacy
````

`scripts/debug_food_group_exclusions.py` is the companion diagnostic. It lists, per meal, which ingredients are counted or dropped and why, and ends with every ingredient still missing a food-group classification or a gram conversion:

````bash
python -m scripts.debug_food_group_exclusions
python -m scripts.debug_food_group_exclusions sinigang    # filter by meal name
````

> ⚠️ There is also a `nutrition_evaluation_results_before.csv` in the project root whose purpose/timing hasn't been documented yet — confirm what it's a "before" snapshot of (e.g. before the ingredients-normalization refactor, or before some other change) before treating either CSV as authoritative for the thesis.

> **Interpretation caveat:** the accuracy figure depends directly on `Meal.calories` being a per-serving value, which is not yet verified (see the Known gap under Meals). Do not treat the figure as final until the 1-serving normalization is complete and the evaluation is rerun. The methodology (bands, scaling, classification) was fixed before results were inspected and should not be adjusted to raise the percentage.

---

# ⚠️ Nutrition Methodology & Limitations

To be documented in the thesis methodology chapter and reviewed with the adviser:

- **Composite standard.** PDRI energy values scaled by FAO/WHO/UNU PAL ratios is a composite method, not a single official table.
- **Ulam-only scaling is app-specific.** `ULAM_ENERGY_SHARE` (0.67), the ulam-only Grow/Glow bands, and the staple exclusion are the app's own reconciliation of two whole-plate standards with single-dish meal data.
- **3 meals per day** is assumed for the per-meal target (`MEALS_PER_DAY`); snacks are not modeled.
- **Complete one-dish meals.** Dishes that contain their own staple (e.g. Pancit Bihon, Ukoy, Vegetable Lumpia) are judged as ulams with their Go ingredients ignored, which may misjudge them. Scoring such dishes at plate level is a possible refinement.
- **Ingredient weights are estimates.** Gram conversions for piece/cup units use USDA reference weights and standard culinary conversions; recipe quantities themselves are sample data.
- **Exact-name classification.** Ingredients are matched to `ingredient_food_groups` via the normalized `Ingredient` table; an unclassified or unconvertible ingredient is excluded from proportions, not guessed.
- **Ages below 19** are clamped to the 19–29 PDRI bracket.
- **Calories are provisional** until Week 7 Day 4 (1-serving normalization) is complete.
- **No automated unit tests** for the Nutrition module yet; verification is by hand calculation, Swagger, and the evaluation harness.
- **Food-group cache staleness.** `get_ingredient_food_group_map()` caches at the process level; a food-group row added without a server restart or explicit `refresh=True` won't be picked up automatically.

---

# 🗃️ Database Migrations

Database schema changes are managed using **Alembic**.

Run all migrations:

````bash
alembic upgrade head
````

Check the current migration:

````bash
alembic current
````

Create a migration after modifying SQLAlchemy models:

````bash
alembic revision --autogenerate -m "describe migration"
````

Always review autogenerated migrations before applying them.

The migrations added since Week 7, confirmed linear via `alembic history --verbose` (each revision has exactly one parent — no branches):

````text
aa4a5f458607   add physical_activity_level to profiles
b1c2d3e4f5a6   create ingredient_food_groups (table + initial seed, name-based)
c2d3e4f5a6b7   add missing ingredient_food_groups rows
c7d8e9f0a1b2   rename daily_budget to budget_per_meal on profiles
d2d3e4f5a6b7   create ingredients table and backfill from existing sources
e3d4f5a6b7c8   convert meal_ingredients to FK (ingredient_id)
f4a5b6c7d8e9   convert pantry_items to FK (ingredient_id)
g5b6c7d8e9f0   create ingredient_prices table
h6c7d8e9f0a1   link ingredient_food_groups to ingredients (FK, drops ingredient_name)  ← head
````

The Grocery List feature does **not** require a new migration for its base logic because the current implementation does not introduce a database model or table of its own — its new pricing capability rides on the `ingredient_prices` table added above. The Week 7 past-slot guard and peso-precision fixes are also migration-free — application-layer logic, no schema changes.

---

# ⚙️ Installation

Clone the repository:

````bash
git clone https://github.com/<username>/TipidMeal-Backend.git
````

Create a virtual environment:

````bash
python -m venv venv
````

Activate it.

Windows:

````bash
venv\Scripts\activate
````

Install dependencies:

````bash
pip install -r requirements.txt
````

> **Windows users:** Python's `zoneinfo` relies on the OS having an IANA
> timezone database, which Windows doesn't ship with (unlike Linux/macOS).
> Install the `tzdata` package (already listed in `requirements.txt`) or
> any `TIMEZONE`-dependent code — such as the Meal Planner past-slot guard
> in `core/utils.py` — will raise `ZoneInfoNotFoundError: 'No time zone
> found with key Asia/Manila'` at request time.

Create a `.env` file.

Example:

````env
PROJECT_NAME=TipidMeal API
PROJECT_VERSION=1.0.0
API_V1_PREFIX=/api/v1
DEBUG=True
TIMEZONE=Asia/Manila

DATABASE_URL=your_database_url

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
````

Never commit `.env` or Supabase secrets to the repository.

Run pending migrations after cloning. A fresh database needs them for `physical_activity_level`, `budget_per_meal`, the normalized `ingredients`/`ingredient_prices` tables, and the FK-based `ingredient_food_groups` and its seed data (without the seed, the Nutrition module classifies no ingredients):

````bash
alembic upgrade head
````

---

# ▶️ Running the Server

Start the development server:

````bash
uvicorn app.main:app --reload
````

The API will be available at:

````text
http://127.0.0.1:8000
````

---

# 📖 API Documentation

Swagger UI:

````text
http://127.0.0.1:8000/docs
````

ReDoc:

````text
http://127.0.0.1:8000/redoc
````

Swagger UI can be used to inspect and manually test API endpoints.

---

# 📌 Current Backend Status

The current backend implementation includes:

````text
Authentication                        ✅
Supabase JWT Verification             ✅
Profile Management                    ✅
Profile Image Upload                  ✅
Physical Activity Level               ✅
Budget Per Meal (renamed)             ✅
Food Allergies                        ✅
Disliked Ingredients                  ✅
Ingredients Normalized (FK-based)     ✅
Ingredient Prices (reference data)    ✅ — seed status unconfirmed
Meals                                  ✅
Meal Ingredients (FK-based)            ✅
Meal Instructions                      ✅
Meal Servings Normalization (1-serv)   🔲 Not yet done — sample data
Ingredient Suggestions                 ✅
Pantry Management                      ✅
Pantry Quantity Handling               ✅
Pantry Ingredients (FK-based)          ✅
Ingredient Substitutions               ✅ (still name-based)
Recommendation Rules                   ✅
Recommendation Scoring                 ✅
Recommendation Affordability Filter    ✅
Recommendation Cost-Based Sort         ✅
Cooking Skill Scoring (manually verified) ✅
Ingredient Availability                ✅
TF-IDF Ingredient Coverage             ✅
Recommendation API                     ✅
Meal Planner                           ✅
Meal Plan CRUD                         ✅
Meal Plan Authentication               ✅
Meal Plan User Isolation               ✅
Meal Plan Past-Slot Guard              ✅
Peso Precision (Weekly Total)          ✅
Grocery List                           ✅
Grocery List Aggregation               ✅
Grocery List Pantry Comparison         ✅
Grocery List Unit Safety               ✅
Grocery List Pricing                   ✅ — see seed-data caveat above
Grocery List Date Range                ✅
Grocery List Authentication            ✅
Grocery List User Isolation            ✅
Favorites                              ✅
Favorites CRUD (Add/List/Remove)       ✅
Favorites Idempotency                  ✅
Favorites Authentication               ✅
Favorites User Isolation               ✅
Daily Caloric Requirement (PDRI x PAL) ✅
Per-Meal Caloric Adequacy              ✅
Ingredient Food Groups (FK-based)      ✅
Food-Group Adequacy (ulam-only)        ✅
Nutrition Endpoint                     ✅
Nutrition on Recommendations           ✅
Nutrition Evaluation Harness           ✅
Nutrition Results Final                🔲 Pending Day 4 data verification + rerun
Nutrition Unit Tests                   🔲 Not yet done
Alembic Migrations                     ✅ — chain order pending confirmation
````

The backend currently provides the core API and database functionality required by the TipidMeal application, plus the Week 8 Nutrition module, its evaluation harness, a normalized ingredient reference layer shared across Meals/Pantry/Nutrition, and optional grocery-list pricing. Week 7's Meal Servings normalization (Part 5 / Day 4) is the one item from the Week 7 plan not yet implemented — current seed data remains sample data, not yet corrected to a 1-serving baseline — and the nutritional-adequacy results should be considered final only once it is done and the evaluation is rerun.

---

# 🧠 Recommendation Approach

The recommendation engine is intentionally deterministic.

The current system uses:

````text
Profile
+
Pantry
+
Meals
+
Ingredient Substitutions
+
Business Rules
+
TF-IDF Ingredient Coverage
+
Weighted Scoring
+
Affordability Hard Filter (Week 7)
````

This approach provides predictable and explainable recommendations. The Nutrition module (Week 8) is equally deterministic: every verdict traces back to published Philippine standards and explicit, documented scaling choices.

An external AI API is not required for the current recommendation implementation.

---

# 🧠 Overall TipidMeal Feature Flow

The current backend supports the following overall application workflow:

````text
                    Supabase Auth
                         ↓
                      Profile
                         ↓
        ┌────────────────┼────────────────┬──────────────┐
        ↓                ↓                ↓              ↓
     Pantry            Meals        Recommendations   Favorites
        │                │                │
        │                └────────────────┘
        │                         ↓
        │                  Recommended Meals ──→ Nutrition Adequacy
        │                         ↓
        └──────────────→  Meal Planner
                                ↓
                         Planned Meals
                                ↓
                         Meal Ingredients
                                ↓
                         Grocery List (+ pricing)
                                ↓
                       Missing Ingredients
                                ↓
                             Shopping
````

This creates the core TipidMeal workflow:

````text
Discover
   ↓
Plan (or Favorite for later)
   ↓
Check Pantry
   ↓
Generate Grocery List (with cost estimate)
   ↓
Shop
   ↓
Cook
````

Nutritional adequacy is computed per meal for the authenticated user and shown alongside meals and recommendations; it informs the user's choice but does not alter the Discover → Plan → Shop flow. Ingredients themselves are now a shared, normalized reference layer underneath Meals, Pantry, Nutrition, and Grocery List.

---

# 📄 License

This project is developed as part of an undergraduate thesis.