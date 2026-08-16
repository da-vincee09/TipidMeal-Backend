# TipidMeal Backend

Backend API for **TipidMeal**, a mobile application that helps users discover affordable, personalized meal recommendations based on their budget, cooking skills, dietary restrictions, ingredient preferences, and available pantry ingredients.

Built with **FastAPI**, **SQLAlchemy 2.0**, **PostgreSQL (Supabase)**, and **Supabase Auth**.

---

## 🚀 Tech Stack

* **FastAPI** – REST API framework
* **SQLAlchemy 2.0** – ORM
* **PostgreSQL (Supabase)** – Database
* **Supabase Auth** – User authentication
* **Supabase Storage** – Profile image storage
* **Pydantic v2** – Data validation
* **JWT / JWKS** – Supabase access-token verification
* **Alembic** – Database migrations
* **python-jose** – JWT verification
* **python-multipart** – Multipart/form-data parsing for profile image uploads

---

## 📁 Project Structure

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
│   └── recommendations/
│       ├── models/
│       │   └── ingredient_substitution.py
│       ├── schemas.py
│       ├── rules.py
│       ├── scoring.py
│       ├── tfidf.py
│       ├── utils.py
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
```

---

# ✅ Implemented Features

## 🔐 Authentication

Authentication is handled by **Supabase Auth**.

FastAPI verifies Supabase access tokens using Supabase's **JWKS endpoint** and the current **ES256 / P-256** signing key.

Implemented:

* Supabase JWT verification
* JWKS public-key retrieval
* ES256 signature verification
* Current authenticated-user dependency
* Protected API routes
* Authentication failure handling

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

The authenticated Supabase UUID is used as the identity source for application-level data.

---

# 👤 Profile Module

The profile module provides user-profile functionality, including profile pictures and dietary preferences.

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

The profile module follows a layered architecture:

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

Implemented:

* SQLAlchemy models
* Pydantic schemas
* Repository layer
* Service layer
* API router
* Profile creation
* Profile retrieval
* Profile updates
* Food allergy relationships
* Disliked ingredient relationships
* Profile picture upload
* Supabase Storage integration

---

# 🥫 Pantry Module

The pantry module represents the ingredients currently available to an authenticated user.

Example:

```text
User Pantry

Rice        2 kg
Chicken     1 kg
Eggs        6 pcs
Tomato      4 pcs
```

Each pantry item is associated with the user's application profile.

Implemented:

* Pantry item SQLAlchemy model
* Pantry item schemas
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

The pantry is also used as an input to the recommendation system.

### Pantry Quantity Handling

The recommendation system now represents pantry availability using both **ingredient name and unit**.

For example:

```text
Pantry

Rice
  kg → 2

Eggs
  pcs → 6

Tomato
  pcs → 4
```

Multiple pantry entries for the same ingredient and unit are combined.

For example:

```text
Rice
2 kg
+
1 kg
=
3 kg
```

Different units are kept separately because the backend does not currently perform automatic unit conversion.

For example:

```text
Rice
kg → 2
g  → 500
```

These values are not automatically converted into a common unit.

---

# 🍽️ Meals Module

The meals module provides the application's meal database.

A meal contains information such as:

* Name
* Description
* Image URL
* Estimated Cost
* Cooking Time
* Difficulty
* Servings
* Calories

Meals are connected to their ingredients and cooking instructions.

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
* Meal schemas
* Repository layer
* Service layer
* API router
* Meal retrieval
* Meal detail retrieval
* Ingredient relationships
* Instruction relationships
* Ingredient suggestion search

The meal database serves as the source of candidate meals for the recommendation system.

---

## 🔎 Ingredient Suggestions

The Meals module provides an ingredient suggestion endpoint for searching existing meal ingredients.

```text
GET /api/v1/meals/ingredients/suggestions?search=tom
```

The endpoint:

* Accepts a search string
* Performs case-insensitive matching
* Returns distinct ingredient names
* Sorts results alphabetically
* Limits results to 10 suggestions by default

Example:

```text
GET /api/v1/meals/ingredients/suggestions?search=tom
```

Possible response:

```json
[
  "Tomato",
  "Tomato Sauce",
  "Tomato Paste"
]
```

This endpoint can be used by the Flutter application for ingredient autocomplete and search functionality.

---

# 🤖 Recommendation Module

The recommendation system currently uses a **deterministic, rule-based approach** rather than an external AI API.

This is intentional.

The recommendation pipeline combines:

```text
Profile
   +
Pantry
   +
Meals
   +
Recommendation Rules
   ↓
Scoring
   ↓
Ranking
   ↓
Recommended Meals
```

Recommendations consider:

* Ingredient availability
* Pantry ingredient quantities
* Ingredient units
* Ingredient substitutions
* Estimated meal cost
* User daily budget
* Cooking skill
* Food allergies
* Disliked ingredients
* Ingredient coverage

---

## Recommendation Scoring

The current hybrid scoring system uses the following components:

| Factor                | Weight |
| --------------------- | -----: |
| Ingredient Coverage   |    30% |
| Budget Compatibility  |    30% |
| Cooking Skill         |    10% |
| Allergy Compatibility |    20% |
| Disliked Ingredients  |    10% |

The final score is calculated deterministically and is therefore explainable during evaluation and thesis defense.

Allergy conflicts are treated as a hard restriction and result in a score of `0`.

Meals that contain required ingredients that cannot be obtained or substituted are treated as fallback candidates and are excluded from the primary recommendation results.

---

# 🧩 Ingredient Adaptation

The recommendation system supports ingredient adaptation through substitution rules.

For example:

```text
Required:
Tomato

User has:
Tomato Sauce

Substitution rule:
Tomato → Tomato Sauce
```

Ingredients can now be classified as:

```text
retain
substitute
insufficient
omit
unavailable
```

### Retain

An ingredient is retained when the pantry contains the ingredient.

If the pantry and recipe use the same unit, the available quantity is checked against the required quantity.

Example:

```text
Required:
Rice → 500 g

Pantry:
Rice → 1 kg

Result:
retain
```

### Insufficient

An ingredient is classified as `insufficient` when:

* The ingredient exists in the pantry.
* The pantry unit matches the recipe unit.
* The pantry quantity is less than the required quantity.

Example:

```text
Required:
Rice → 1 kg

Pantry:
Rice → 500 g

Result:
insufficient
```

The response includes quantity information:

```json
{
  "ingredient": "Rice",
  "action": "insufficient",
  "available_quantity": 500,
  "required_quantity": 1000,
  "unit": "g"
}
```

An `insufficient` ingredient is treated as a **soft warning** rather than an unavailable ingredient.

It does not automatically cause the meal to become a fallback candidate.

### Different Units

The backend does not currently perform automatic unit conversion.

For example:

```text
Pantry:
Rice → 1 kg

Recipe:
Rice → 500 g
```

Because the units differ, the backend does not attempt to determine whether the quantity is sufficient.

Instead, the ingredient is retained because the ingredient itself exists in the pantry.

This avoids unsafe quantity comparisons without a reliable unit-conversion system.

### Unavailable

An ingredient is classified as `unavailable` when it is not present in the pantry and cannot be substituted.

Only a true `unavailable` ingredient can cause a meal to become a fallback candidate.

---

# 🧠 Recommendation Availability Model

The recommendation service now represents pantry availability as:

```text
Ingredient
    ↓
Unit
    ↓
Quantity
```

Conceptually:

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

This allows the recommendation system to distinguish between:

```text
Ingredient exists
        ↓
Does the unit match?
        ↓
Yes → Compare quantity
        ↓
Enough? ── Yes → retain
        │
        └── No → insufficient
```

If the units do not match:

```text
Ingredient exists
        ↓
Different units
        ↓
Cannot safely compare
        ↓
retain
```

If the ingredient does not exist:

```text
Ingredient missing
        ↓
Check substitution
        ↓
Substitution exists → substitute
        ↓
No substitution → unavailable
```

---

## TF-IDF Ingredient Coverage

The recommendation system also includes a TF-IDF-based ingredient weighting component.

Instead of treating every ingredient as equally important, ingredient coverage can account for ingredient importance within the meal corpus.

This provides a more meaningful measure of how well the user's available ingredients match a meal.

The system currently combines this ingredient coverage with the other deterministic scoring components.

Quantity sufficiency is handled separately from the name-based ingredient coverage calculation.

---

# 📡 API Endpoints

The backend exposes versioned routes under:

```text
/api/v1
```

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

Recommendation routes are protected using the authenticated Supabase user.

---

# 🔒 Authorization and User Isolation

Protected endpoints use:

```text
Authorization: Bearer <Supabase Access Token>
```

The backend resolves the authenticated Supabase UUID through:

```text
JWT
 ↓
get_current_user()
 ↓
auth_id
 ↓
Profile
 ↓
User-owned data
```

User-specific resources such as profiles and pantry items are associated with the authenticated user's profile.

A user must not be able to access another user's application data by manually providing another user's identifier.

---

# 🖼️ Profile Images

Profile images are stored using **Supabase Storage** in a public bucket named:

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
Flutter
    ↓
Pick image locally
    ↓
Create/update profile
    ↓
POST /profiles/me/image
    ↓
FastAPI
    ↓
Supabase Storage
    ↓
Public image URL
    ↓
Profile.profile_image_url
```

The upload endpoint is intentionally separate from normal profile creation and update operations.

This allows profile data to be saved independently from a potentially failed image upload.

---

# 🗄️ Database

Database provider:

**Supabase PostgreSQL**

Current application data includes:

```text
profiles
   │
   ├── food_allergies
   │
   ├── disliked_ingredients
   │
   └── pantry_items

meals
   │
   ├── meal_ingredients
   │
   └── meal_instructions

ingredient_substitutions
```

The application uses relational foreign keys and cascading relationships where appropriate.

The `profiles.auth_id` field stores the authenticated Supabase user's UUID.

---

# 🔄 Recommendation Data Flow

The current deterministic recommendation flow is:

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
      ├── Available Ingredients
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
Recommendations
```

---

# 🧪 Current Backend Testing Status

The backend modules can be imported and tested independently before frontend integration.

The recommendation service can be executed directly against the database.

### Empty Pantry

An empty pantry results in no primary recommendations when meals contain unavailable required ingredients.

Example:

```text
Pantry:
{}

Meal:
Chicken Adobo

Required ingredient:
Chicken

Result:
unavailable → fallback
```

### Sufficient Quantity

```text
Pantry:
Rice → 2 kg

Recipe:
Rice → 500 g

Result:
retain
```

### Insufficient Quantity

```text
Pantry:
Rice → 500 g

Recipe:
Rice → 1 kg

Result:
insufficient
```

The meal does not automatically become a fallback candidate because the ingredient exists in the user's pantry.

### Different Units

```text
Pantry:
Rice → 1 kg

Recipe:
Rice → 500 g

Result:
retain
```

The backend does not perform automatic unit conversion.

Once the Flutter pantry screen is implemented and the authenticated user adds ingredients, the recommendation endpoint can be tested end-to-end using real user data.

---

# 📱 Frontend Integration Status

The backend foundation for the following features is implemented:

```text
Authentication           ✅
Profile                  ✅
Profile Image            ✅
Meals Backend            ✅
Ingredient Suggestions   ✅
Pantry Backend           ✅
Pantry Quantity Handling ✅
Recommendation Rules     ✅
Ingredient Substitution  ✅
Recommendation Scoring   ✅
TF-IDF Coverage          ✅
Recommendation API       ✅
```

The next development phase is connecting these backend features to Flutter.

Planned Flutter features:

```text
features/
├── authentication/
├── profile/
├── home/
├── pantry/
├── meals/
└── recommendations/
```

The Flutter application will communicate with FastAPI using authenticated Supabase access tokens.

The next integration flow is:

```text
Flutter
   ↓
Supabase Auth
   ↓
Access Token
   ↓
FastAPI
   ↓
Pantry / Meals / Recommendations
   ↓
Supabase PostgreSQL
```

---

# 🧠 AI Recommendation

An external AI API is **not currently required** for the recommendation engine.

The first implementation is intentionally deterministic:

```text
Profile
+
Pantry
+
Meals
+
Explicit Business Rules
+
Scoring
```

This provides an explainable recommendation system suitable for thesis evaluation.

AI-based functionality can be evaluated and added later if it provides a meaningful improvement to the recommendation system.

---

# 🚧 Remaining Development

The major remaining work for this development phase is frontend integration.

## Flutter

* Pantry feature
* Pantry screen
* Add/edit/delete pantry items
* Ingredient autocomplete using the ingredient suggestion endpoint
* Meals feature
* Meal list screen
* Meal detail screen
* Recommendations feature
* Recommendation screen
* Recommendation cards
* Home screen integration
* API datasource implementations
* Repository implementations
* Providers/state management
* Authenticated API requests
* Loading states
* Error states
* Empty-state handling

## Integration Testing

After Flutter integration:

* Authentication → Home
* Home → Pantry
* Pantry → Recommendations
* Recommendations → Meal Detail
* Profile → Recommendations
* Ingredient autocomplete
* JWT protection
* User isolation
* Empty pantry
* Empty recommendations
* Insufficient pantry quantities
* Different pantry units
* Ingredient substitutions
* API errors
* Loading states
* Database behavior

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

`SUPABASE_SERVICE_ROLE_KEY` is required for server-side profile image uploads.

It must never be exposed to the Flutter client or committed to the repository.

Do not commit `.env` or any Supabase secrets.

---

# 🗃️ Database Migrations

Database schema changes are managed using **Alembic**.

Run migrations with:

```bash
alembic upgrade head
```

Create a new migration after model changes with:

```bash
alembic revision --autogenerate -m "describe migration"
```

Always review generated migrations before applying them.

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

The Swagger documentation can be used to inspect and manually test the backend endpoints.

---

# 📌 Development Status

Current **Week 2 backend status**:

```text
Authentication                ✅
Profile                       ✅
Profile Image                 ✅
Meals                         ✅
Ingredient Suggestions        ✅
Pantry                        ✅
Pantry Quantity Handling      ✅
Recommendation Rules          ✅
Recommendation Scoring        ✅
Ingredient Substitution       ✅
Ingredient Availability       ✅
TF-IDF Coverage               ✅
Recommendation API            ✅
Flutter Pantry Integration    ⏳
Flutter Meals Integration     ⏳
Flutter Recommendations      ⏳
Home Integration              ⏳
End-to-End Testing            ⏳
```

The Week 2 backend provides the core foundation for personalized meal recommendations, including pantry-aware ingredient availability, quantity-aware matching, ingredient substitutions, deterministic scoring, TF-IDF ingredient coverage, and ingredient autocomplete.

The next major development phase is Flutter integration and end-to-end testing.

---

## 📄 License

This project is developed as part of an undergraduate thesis.
