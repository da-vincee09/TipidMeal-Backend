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
* **python-multipart** – Multipart/form-data parsing, required for the profile image upload endpoint

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
│   ├── storage/
│   │   └── supabase_storage.py
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

> The Flutter app is now fully connected to this backend — login, signup, and every profile operation (including image upload) route through the Supabase-token-verified endpoints below.

---

## 👤 Profile Module

The profile module provides the application's user-profile functionality, including profile pictures.

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

Image uploads follow a parallel, separate path that doesn't go through the repository/service layers used for the rest of the profile, since it's a file operation against Supabase Storage rather than a database write:

```text
Router (POST /profiles/me/image)
  ↓
shared/storage/supabase_storage.py  →  Supabase Storage (REST API,
  ↓                                      service-role key, public bucket)
Profile row updated directly with the
returned public URL, then committed
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
* **Profile picture upload**, storage, and persistence

---

## 🔐 Protected Endpoints

| Method | Endpoint                     | Description                                          |
| ------ | ----------------------------- | ----------------------------------------------------- |
| POST   | `/api/v1/profiles`            | Create the authenticated user's profile               |
| GET    | `/api/v1/profiles/me`         | Retrieve the authenticated user's profile              |
| PUT    | `/api/v1/profiles/me`         | Update the authenticated user's profile                |
| POST   | `/api/v1/profiles/me/image`   | Upload/replace the authenticated user's profile picture |

Authentication is required using:

```text
Authorization: Bearer <Supabase Access Token>
```

Unauthenticated requests are rejected with:

```text
401 Unauthorized
```

`POST /profiles/me/image` additionally requires that a profile already exists for the authenticated user — it returns `404 Not Found` otherwise, since there is no profile row yet to attach the image URL to. On the client, this endpoint is only called as a follow-up step, after `POST /profiles` or `PUT /profiles/me` has already succeeded.

The image endpoint also validates:

* **Content type** — only `image/jpeg`, `image/png`, `image/webp` are accepted (`422 Unprocessable Entity` otherwise)
* **File size** — 5 MB maximum, matching the Supabase Storage bucket's own limit (`422` otherwise)

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

Profile images are stored using **Supabase Storage**, in a **public** bucket named `profile-images` (5 MB limit, `image/jpeg` / `image/png` / `image/webp` only — enforced both by the bucket configuration and by the API).

Actual implemented flow:

```text
Flutter
    ↓
Pick image locally (image_picker) — no upload yet
    ↓
Submit profile form → POST /profiles or PUT /profiles/me
    ↓
On success, upload the picked image:
    POST /profiles/me/image  (multipart/form-data)
    ↓
FastAPI → shared/storage/supabase_storage.py
    ↓
Supabase Storage REST API (raw `requests` call, authenticated
with the service-role key — no supabase-py client dependency,
consistent with how shared/auth/jwt.py talks to Supabase's
JWKS endpoint directly)
    ↓
Object written to the profile-images bucket at "{auth_id}.{ext}"
(one object per user; re-uploads overwrite via x-upsert)
    ↓
Public URL constructed and saved onto the profile row
    ↓
{"profile_image_url": "..."} returned to Flutter
```

The upload is deliberately a **separate endpoint** from profile create/update, not combined multipart handling on those routes — this keeps `POST /profiles` and `PUT /profiles/me` as plain JSON endpoints, and lets the client treat a failed image upload as non-fatal (the rest of the profile is already saved) rather than needing to retry the whole form.

The `profile_image_url` field is supported by the profile model and schemas, and is populated automatically by the upload endpoint — no separate client-side step is needed to persist the URL.

---

## 📌 Current API Flow

The complete, connected application flow is:

```text
Flutter
      ↓
Supabase Auth
      ↓
JWT Access Token
      ↓
FastAPI
      ↓
JWT Verification (JWKS / ES256)
      ↓
Current User Dependency
      ↓
Profile Service  ──────────────┐
      ↓                        │
Repository                     │ (image uploads only)
      ↓                        ▼
Supabase PostgreSQL   shared/storage/supabase_storage.py
                                ↓
                        Supabase Storage
```

The backend authentication layer, profile CRUD, and profile image upload are all implemented and connected end-to-end to the Flutter client.

---

## 🚧 Planned Features

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

If `python-multipart` isn't already listed, install it separately (required for the profile image upload endpoint):

```bash
pip install python-multipart
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

`SUPABASE_SERVICE_ROLE_KEY` is required for profile image uploads — it authenticates server-side writes to Supabase Storage and bypasses Row Level Security. It is **not** the same as the `anon` key used client-side by the Flutter app, and it must never be exposed to the client or committed to the repository.

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