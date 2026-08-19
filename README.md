# TipidMeal Backend

Backend API for **TipidMeal**, a mobile application that helps users discover affordable, personalized meals based on their budget, cooking skills, dietary restrictions, ingredient preferences, pantry availability, meal-planning needs, grocery requirements, and saved favorites.

Built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL (Supabase)**, **Supabase Auth**, and **Alembic**.

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
│   ├── database.py
│   └── dependencies.py
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
│   └── favorites/
│       ├── models/
│       │   ├── __init__.py
│       │   └── favorite.py
│       ├── schemas.py
│       ├── repository.py
│       ├── service.py
│       └── router.py
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
Meal Planner + Meals + Pantry
   ↓
Computed Grocery List
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

Each major feature is isolated inside its own module.

Current backend modules:

````text
Profiles
Pantry
Meals
Recommendations
Meal Planner
Grocery List
Favorites
````

Shared functionality such as authentication, database configuration, storage, and common schemas is placed inside `shared/`.

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
* Daily Budget
* Cooking Skill Level
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

Profile architecture:

````text
Authenticated User
       ↓
Profile
       ├── Food Allergies
       └── Disliked Ingredients
````

The profile data is used by the recommendation system to personalize meal recommendations.

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
Pantry Items
       ↓
PostgreSQL
````

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
 ├── Meal Ingredients
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
Ingredient Adaptation
   ↓
Scoring
   ↓
Ranking
   ↓
Recommended Meals
````

Recommendations consider:

* Ingredient availability
* Pantry quantities
* Ingredient units
* Ingredient substitutions
* Estimated meal cost
* User daily budget
* Cooking skill
* Food allergies
* Disliked ingredients
* Ingredient coverage

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

Allergy conflicts are treated as hard restrictions.

A meal containing an allergy conflict receives:

````text
score = 0
````

The recommendation system is deterministic and explainable, which is useful for evaluation and thesis defense.

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

Unavailable required ingredients can cause a meal to become a fallback candidate.

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

---

# 🛒 Grocery List Module

The Grocery List is a **derived feature** that converts a user's meal plan into a list of ingredients that need to be purchased.

The feature connects the Meal Planner, Meals, and Pantry modules.

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
Grocery List
````

The Grocery List does **not** introduce a new SQLAlchemy model or database table in the current implementation.

Instead, the list is computed whenever the endpoint is requested.

This keeps the grocery list synchronized with the latest:

* Meal Plan
* Meal Ingredients
* Pantry contents

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
Grocery List Service
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

# 🧾 Grocery List Schemas

The Grocery List response contains information necessary for the frontend to display the shopping requirements.

A Grocery List item contains:

````text
Ingredient
Unit
Required Quantity
Pantry Quantity
Quantity to Buy
````

Conceptually:

````json
{
  "ingredient": "Chicken",
  "unit": "g",
  "required_quantity": 1000,
  "pantry_quantity": 500,
  "quantity_to_buy": 500
}
````

The overall response also contains the date range covered by the grocery list.

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
Grocery List
````

This makes the Grocery List the final derived feature of the Pantry + Meals + Meal Planner workflow.

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

# 📡 API Endpoints

All API routes are versioned under:

````text
/api/v1
````

---

## Profiles

| Method | Endpoint                    | Description                           |
| ------ | ---------------------------- | -------------------------------------- |
| POST   | `/api/v1/profiles`          | Create authenticated user's profile   |
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

## Recommendations

| Method | Endpoint                  | Description                                |
| ------ | -------------------------- | -------------------------------------------- |
| GET    | `/api/v1/recommendations` | Generate personalized meal recommendations |

---

## Meal Planner

| Method | Endpoint                    | Description                |
| ------ | ---------------------------- | ---------------------------- |
| POST   | `/api/v1/meal-planner`      | Create a meal plan entry   |
| GET    | `/api/v1/meal-planner`      | Retrieve meal plan entries |
| GET    | `/api/v1/meal-planner/{id}` | Retrieve a meal plan entry |
| PUT    | `/api/v1/meal-planner/{id}` | Update a meal plan entry   |
| DELETE | `/api/v1/meal-planner/{id}` | Delete a meal plan entry   |

Meal Planner routes are protected using the authenticated Supabase user.

---

## Grocery List

| Method | Endpoint                                     | Description                                     |
| ------ | ---------------------------------------------- | -------------------------------------------------- |
| GET    | `/api/v1/grocery-list`                       | Generate grocery list for the current week      |
| GET    | `/api/v1/grocery-list?start_date=&end_date=` | Generate grocery list for a specific date range |

The Grocery List endpoint is protected using the authenticated Supabase user.

The list is calculated dynamically from:

````text
Meal Plan
+
Meal Ingredients
+
Pantry
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

This allows the Grocery List to remain a live derived view.

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
   └── pantry_items

meals
   │
   ├── meal_ingredients
   └── meal_instructions

ingredient_substitutions

meal_plan_entries

favorites
````

There is currently **no `grocery_list_items` table**.

The Grocery List is computed dynamically from existing data.

Main relationships:

````text
Profile
 ├── Pantry Items
 ├── Food Allergies
 ├── Disliked Ingredients
 ├── Meal Plan Entries
 └── Favorites

Meal
 ├── Meal Ingredients
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
        ↓
Computed Grocery List
````

Foreign keys and cascading behavior are defined at the database level where appropriate.

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
      ├── Daily Budget
      ├── Cooking Skill
      ├── Allergies
      └── Disliked Ingredients
      │
      ↓
Pantry
      │
      ├── Ingredients
      ├── Quantities
      └── Units
      │
      ↓
Meals
      │
      ├── Ingredients
      ├── Cost
      └── Difficulty
      │
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
Allergy Filtering
      ↓
Disliked Ingredient Score
      ↓
Hybrid Score
      ↓
Ranking
      ↓
Recommended Meals
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
Grocery List
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

Grocery List validation:

````bash
python -c "from features.grocery_list.schemas import GroceryListItem, GroceryListResponse; print('Grocery list schemas OK')"
````

````bash
python -c "from features.grocery_list.service import get_grocery_list; print('Grocery list service OK')"
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

The complete FastAPI application can be verified with:

````bash
python -c "from app.main import app; print('FastAPI app OK')"
````

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

The current database includes the Meal Planner migration:

````text
31b00c8d3565
create meal plan entries
````

and the Favorites migration:

````text
2e7b4adc1b5d
create favorites table
````

The Grocery List feature does **not** require a new migration because the current implementation does not introduce a database model or table.

Migration chain:

````text
Ingredient Substitutions
        ↓
Meal Plan Entries
        ↓
Favorites
````

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
Authentication                  ✅
Supabase JWT Verification       ✅
Profile Management              ✅
Profile Image Upload            ✅
Food Allergies                  ✅
Disliked Ingredients            ✅
Meals                            ✅
Meal Ingredients                 ✅
Meal Instructions                ✅
Ingredient Suggestions           ✅
Pantry Management                ✅
Pantry Quantity Handling         ✅
Ingredient Substitutions         ✅
Recommendation Rules             ✅
Recommendation Scoring           ✅
Ingredient Availability          ✅
TF-IDF Ingredient Coverage       ✅
Recommendation API               ✅
Meal Planner                     ✅
Meal Plan CRUD                   ✅
Meal Plan Authentication         ✅
Meal Plan User Isolation         ✅
Grocery List                     ✅
Grocery List Aggregation         ✅
Grocery List Pantry Comparison   ✅
Grocery List Unit Safety         ✅
Grocery List Date Range          ✅
Grocery List Authentication      ✅
Grocery List User Isolation      ✅
Favorites                        ✅
Favorites CRUD (Add/List/Remove) ✅
Favorites Idempotency            ✅
Favorites Authentication         ✅
Favorites User Isolation         ✅
Alembic Migrations               ✅
````

The backend currently provides the core API and database functionality required by the TipidMeal application.

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
````

This approach provides predictable and explainable recommendations.

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
        │                  Recommended Meals
        │                         ↓
        └──────────────→  Meal Planner
                                ↓
                         Planned Meals
                                ↓
                         Meal Ingredients
                                ↓
                         Grocery List
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
Generate Grocery List
   ↓
Shop
   ↓
Cook
````

---

# 📄 License

This project is developed as part of an undergraduate thesis.