# TipidMeal Backend

Backend API for **TipidMeal**, a mobile application that helps users discover affordable, personalized meals based on their budget, cooking skills, dietary restrictions, ingredient preferences, pantry availability, and meal-planning needs.

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

```text
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
│   └── meal_planner/
│       ├── models/
│       │   ├── __init__.py
│       │   └── meal_plan_entry.py
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

```text
Router
   ↓
Service
   ↓
Repository
   ↓
SQLAlchemy Models
   ↓
PostgreSQL
```

Each major feature is isolated inside its own module.

Current backend modules:

```text
Profiles
Pantry
Meals
Recommendations
Meal Planner
```

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

```text
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
```

The authenticated Supabase UUID is used as the identity source for application-level user data.

Protected requests use:

```text
Authorization: Bearer <Supabase Access Token>
```

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

```text
Authenticated User
       ↓
Profile
       ├── Food Allergies
       └── Disliked Ingredients
```

The profile data is used by the recommendation system to personalize meal recommendations.

---

# 🥫 Pantry Module

The pantry module represents ingredients currently available to an authenticated user.

Example:

```text
Rice        2 kg
Chicken     1 kg
Eggs        6 pcs
Tomato      4 pcs
```

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

```text
Authenticated User
       ↓
Profile
       ↓
Pantry Items
       ↓
PostgreSQL
```

## Pantry Quantity Handling

Pantry availability is represented using:

```text
Ingredient
    ↓
Unit
    ↓
Quantity
```

Example:

```python
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
```

Multiple pantry entries for the same ingredient and unit can be combined.

For example:

```text
Rice
2 kg
+
1 kg
=
3 kg
```

Different units are kept separately.

For example:

```text
Rice
kg → 2
g  → 500
```

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

```text
Meal
 │
 ├── Meal Ingredients
 │
 └── Meal Instructions
```

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

```text
GET /api/v1/meals/ingredients/suggestions?search=tom
```

The endpoint:

* Accepts a search string
* Performs case-insensitive matching
* Returns distinct ingredient names
* Sorts results alphabetically
* Limits results to 10 suggestions by default

Example response:

```json
[
  "Tomato",
  "Tomato Paste",
  "Tomato Sauce"
]
```

---

# 🤖 Recommendation Module

The recommendation system uses a deterministic, rule-based approach.

No external AI API is required for the current recommendation engine.

The recommendation pipeline is:

```text
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
```

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

```text
score = 0
```

The recommendation system is deterministic and explainable, which is useful for evaluation and thesis defense.

---

# 🧩 Ingredient Adaptation

The recommendation system can adapt meal ingredients based on pantry availability and substitution rules.

An ingredient can be classified as:

```text
retain
substitute
insufficient
omit
unavailable
```

## Retain

An ingredient is retained when the ingredient exists in the pantry.

If the pantry and recipe units match, the backend compares quantities.

Example:

```text
Required:
Rice → 500 g

Pantry:
Rice → 1 kg

Result:
retain
```

---

## Insufficient

An ingredient is classified as insufficient when:

* The ingredient exists in the pantry.
* The units match.
* The pantry quantity is lower than the required quantity.

Example:

```text
Required:
Rice → 1 kg

Pantry:
Rice → 500 g

Result:
insufficient
```

Example response:

```json
{
  "ingredient": "Rice",
  "action": "insufficient",
  "available_quantity": 500,
  "required_quantity": 1000,
  "unit": "g"
}
```

An insufficient ingredient is treated as a soft warning rather than automatically making the meal a fallback candidate.

---

## Different Units

The backend does not currently perform automatic unit conversion.

Example:

```text
Pantry:
Rice → 1 kg

Recipe:
Rice → 500 g
```

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

```text
milk
  ↓
evaporated_milk

butter
  ↓
margarine
```

The substitution system allows the recommendation engine to determine whether an unavailable ingredient can be replaced with another available ingredient.

The database contains an:

```text
ingredient_substitutions
```

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

```text
Profile
   ↓
Meal Plan Entry
   ↓
Meal
```

A meal plan entry contains:

* Meal
* Planned Date
* Meal Slot
* Creation timestamp
* Update timestamp

Example:

```text
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
```

The database model is:

```text
meal_plan_entries
```

with relationships to:

```text
profiles
meals
```

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

# 📡 API Endpoints

All API routes are versioned under:

```text
/api/v1
```

---

## Profiles

| Method | Endpoint                    | Description                           |
| ------ | --------------------------- | ------------------------------------- |
| POST   | `/api/v1/profiles`          | Create authenticated user's profile   |
| GET    | `/api/v1/profiles/me`       | Retrieve authenticated user's profile |
| PUT    | `/api/v1/profiles/me`       | Update authenticated user's profile   |
| POST   | `/api/v1/profiles/me/image` | Upload/replace profile picture        |

---

## Pantry

| Method | Endpoint              | Description                          |
| ------ | --------------------- | ------------------------------------ |
| POST   | `/api/v1/pantry`      | Add pantry item                      |
| GET    | `/api/v1/pantry`      | Retrieve authenticated user's pantry |
| GET    | `/api/v1/pantry/{id}` | Retrieve pantry item                 |
| PUT    | `/api/v1/pantry/{id}` | Update pantry item                   |
| DELETE | `/api/v1/pantry/{id}` | Delete pantry item                   |

---

## Meals

| Method | Endpoint                                | Description                   |
| ------ | --------------------------------------- | ----------------------------- |
| GET    | `/api/v1/meals`                         | Retrieve available meals      |
| GET    | `/api/v1/meals/ingredients/suggestions` | Search ingredient suggestions |
| GET    | `/api/v1/meals/{meal_id}`               | Retrieve meal details         |

---

## Recommendations

| Method | Endpoint                  | Description                                |
| ------ | ------------------------- | ------------------------------------------ |
| GET    | `/api/v1/recommendations` | Generate personalized meal recommendations |

---

## Meal Planner

| Method | Endpoint                    | Description                |
| ------ | --------------------------- | -------------------------- |
| POST   | `/api/v1/meal-planner`      | Create a meal plan entry   |
| GET    | `/api/v1/meal-planner`      | Retrieve meal plan entries |
| GET    | `/api/v1/meal-planner/{id}` | Retrieve a meal plan entry |
| PUT    | `/api/v1/meal-planner/{id}` | Update a meal plan entry   |
| DELETE | `/api/v1/meal-planner/{id}` | Delete a meal plan entry   |

Meal Planner routes are protected using the authenticated Supabase user.

---

# 🔒 Authorization and User Isolation

Protected endpoints use:

```text
Authorization: Bearer <Supabase Access Token>
```

The authentication flow is:

```text
JWT
 ↓
get_current_user()
 ↓
Supabase auth_id
 ↓
Profile
 ↓
User-owned resources
```

User-specific resources are always scoped to the authenticated user's profile.

For example:

```text
Authenticated User
       ↓
Profile
       ↓
Pantry Items
       ↓
Meal Plan Entries
```

A user must not be able to access another user's pantry or meal-plan entries by manually supplying another user's identifier.

---

# 🖼️ Profile Images

Profile images are stored using **Supabase Storage**.

Bucket:

```text
profile-images
```

Supported formats:

* JPEG
* PNG
* WebP

Maximum file size:

```text
5 MB
```

Upload flow:

```text
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
```

The Supabase service-role key is used only on the backend.

It must never be exposed to the client application.

---

# 🗄️ Database

Database provider:

**Supabase PostgreSQL**

Current application tables include:

```text
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
```

Main relationships:

```text
Profile
 ├── Pantry Items
 ├── Food Allergies
 ├── Disliked Ingredients
 └── Meal Plan Entries

Meal
 ├── Meal Ingredients
 ├── Meal Instructions
 └── Meal Plan Entries
```

Foreign keys and cascading behavior are defined at the database level where appropriate.

---

# 🔄 Recommendation Data Flow

```text
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
```

---

# 📅 Meal Planning Data Flow

```text
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
```

Meal-plan entries are scoped to the authenticated user's profile.

---

# 🧪 Backend Testing and Validation

Backend modules can be independently imported and validated before integration testing.

Example validation commands:

```bash
python -c "from features.meal_planner.models import MealPlanEntry; print(MealPlanEntry.__tablename__)"
```

```bash
python -c "from features.meal_planner.schemas import MealPlanEntryCreate, MealPlanEntryUpdate, MealPlanEntryResponse, WeeklyPlanResponse; print('Meal planner schemas OK')"
```

```bash
python -c "from features.meal_planner.repository import create_meal_plan_entry, get_meal_plan_entries, get_meal_plan_entry_by_id, update_meal_plan_entry, delete_meal_plan_entry; print('Meal planner repository OK')"
```

```bash
python -c "from features.meal_planner.service import create_meal_plan_entry, get_meal_plan_entries, get_meal_plan_entry_by_id, update_meal_plan_entry, delete_meal_plan_entry; print('Meal planner service OK')"
```

```bash
python -c "from features.meal_planner.router import router; print('Meal planner router OK')"
```

The complete FastAPI application can be verified with:

```bash
python -c "from app.main import app; print('FastAPI app OK')"
```

---

# 🗃️ Database Migrations

Database schema changes are managed using **Alembic**.

Run all migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Create a migration after modifying SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe migration"
```

Always review autogenerated migrations before applying them.

The current database includes the Meal Planner migration:

```text
31b00c8d3565
create meal plan entries
```

Migration chain:

```text
Ingredient Substitutions
        ↓
Meal Plan Entries
```

---

# ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/<username>/TipidMeal-Backend.git
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it.

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file.

Example:

```env
PROJECT_NAME=TipidMeal API
PROJECT_VERSION=1.0.0
API_V1_PREFIX=/api/v1
DEBUG=True
TIMEZONE=Asia/Manila

DATABASE_URL=your_database_url

SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

Never commit `.env` or Supabase secrets to the repository.

---

# ▶️ Running the Server

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

# 📖 API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

Swagger UI can be used to inspect and manually test API endpoints.

---

# 📌 Current Backend Status

The current backend implementation includes:

```text
Authentication                 ✅
Supabase JWT Verification      ✅
Profile Management             ✅
Profile Image Upload           ✅
Food Allergies                 ✅
Disliked Ingredients           ✅
Meals                          ✅
Meal Ingredients               ✅
Meal Instructions              ✅
Ingredient Suggestions         ✅
Pantry Management              ✅
Pantry Quantity Handling       ✅
Ingredient Substitutions       ✅
Recommendation Rules           ✅
Recommendation Scoring         ✅
Ingredient Availability        ✅
TF-IDF Ingredient Coverage     ✅
Recommendation API             ✅
Meal Planner                   ✅
Meal Plan CRUD                 ✅
Meal Plan Authentication       ✅
Meal Plan User Isolation       ✅
Alembic Migrations              ✅
```

The backend currently provides the core API and database functionality required by the TipidMeal application.

---

# 🧠 Recommendation Approach

The recommendation engine is intentionally deterministic.

The current system uses:

```text
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
```

This approach provides predictable and explainable recommendations.

An external AI API is not required for the current recommendation implementation.

---

# 📄 License

This project is developed as part of an undergraduate thesis.

