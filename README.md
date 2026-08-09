# TipidMeal Backend

Backend API for **TipidMeal**, a mobile application that helps users discover affordable, personalized meal recommendations based on their budget, cooking skills, dietary preferences, and available ingredients.

Built with **FastAPI**, **SQLAlchemy 2.0**, and **Supabase PostgreSQL**.

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
│   └── profiles/
│       ├── models/
│       │   ├── __init__.py
│       │   ├── profile.py
│       │   ├── food_allergy.py
│       │   └── disliked_ingredient.py
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
│   ├── responses/
│   │   └── base_reponse.py
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

## ✅ Features Implemented

### Authentication

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

> Flutter-side Supabase authentication has not yet been connected to the backend. The backend is prepared to receive and verify the access token.

---

## 👤 Profile Module

The profile module provides the application's initial user-profile functionality.

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
* Profile relationships
* Profile creation
* Profile retrieval
* Profile updates

---

## 🔐 Protected Endpoints

| Method | Endpoint              | Description                               |
| ------ | --------------------- | ----------------------------------------- |
| POST   | `/api/v1/profiles`    | Create the authenticated user's profile   |
| GET    | `/api/v1/profiles/me` | Retrieve the authenticated user's profile |
| PUT    | `/api/v1/profiles/me` | Update the authenticated user's profile   |

Authentication is required using:

```text
Authorization: Bearer <Supabase Access Token>
```

Unauthenticated requests are rejected with:

```text
401 Unauthorized
```

---

## 🗄 Database

Database provider:

* **Supabase PostgreSQL**

Current application tables include:

* `profiles`
* `food_allergies`
* `disliked_ingredients`

The profile relationships are structured as:

```text
profiles
   │
   ├── food_allergies
   │
   └── disliked_ingredients
```

Both related tables reference `profiles.id` and use cascading deletion.

The `profiles.auth_id` field stores the authenticated Supabase user's UUID.

### Database migrations

Database schema changes are managed using **Alembic**.

Implemented migrations include:

* Profile schema updates
* Food allergies table
* Disliked ingredients table
* Related foreign keys and indexes

---

## 🖼 Profile Images

Profile images are intended to be stored using **Supabase Storage**.

Planned flow:

```text
Flutter
    ↓
Upload Image
    ↓
Supabase Storage
    ↓
Receive Image URL
    ↓
FastAPI
    ↓
PUT /profiles/me
    ↓
Store URL in PostgreSQL
```

The `profile_image_url` field is already supported by the profile model and schemas.

---

## 📌 Current API Flow

The intended complete application flow is:

```text
Flutter
      ↓
Supabase Auth
      ↓
JWT Access Token
      ↓
FastAPI
      ↓
JWT Verification
      ↓
Current User Dependency
      ↓
Profile Service
      ↓
Repository
      ↓
Supabase PostgreSQL
```

The backend authentication layer is already prepared for this flow.

---

## 🚧 Planned Features

* Flutter Supabase authentication integration
* Pantry Management
* Ingredient Inventory
* AI Meal Recommendation Engine
* Weekly Meal Planner
* Grocery List Generator
* Saved Meals
* Favorites
* Nutrition Information
* Admin Module

---

## ⚙️ Installation

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
```

The backend retrieves Supabase's public JWT signing keys from:

```text
https://your-project.supabase.co/auth/v1/.well-known/jwks.json
```

> Do not commit `.env` or any Supabase secrets to the repository.

Run the server:

```bash
uvicorn app.main:app --reload
```

---

## 📖 API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## 📄 License

This project is developed as part of an undergraduate thesis.
