# TipidMeal Backend

Backend API for **TipidMeal**, a mobile application that helps users discover affordable, personalized meal recommendations based on their budget, cooking skills, dietary preferences, and available ingredients.

Built with **FastAPI**, **SQLAlchemy**, and **Supabase PostgreSQL**.

---

## 🚀 Tech Stack

- **FastAPI** – REST API framework
- **SQLAlchemy 2.0** – ORM
- **PostgreSQL (Supabase)** – Database
- **Supabase Auth** – User authentication
- **Supabase Storage** – Profile image storage
- **Pydantic v2** – Data validation
- **JWT** – Token verification
- **Alembic** *(planned)* – Database migrations

---

## 📁 Project Structure

```
backend/
│
├── core/
│   ├── database.py
│   ├── dependencies.py
│   └── security.py
│
├── features/
│   └── profiles/
│       ├── models.py
│       ├── schemas.py
│       ├── repository.py
│       ├── service.py
│       └── router.py
│
├── shared/
│   └── database/
│
├── main.py
├── requirements.txt
└── .env
```

---

## ✅ Features Implemented

### Authentication

Authentication is handled by **Supabase Auth**.

The backend verifies JWT access tokens before allowing access to protected endpoints.

Implemented:

- JWT verification
- Current user dependency
- Protected API routes

---

### Profile Module

Implemented CRUD operations for user profiles.

Fields:

- Profile Image URL
- First Name
- Last Name
- Age
- Sex
- Daily Budget
- Cooking Skill Level
- Food Allergies
- Disliked Ingredients

Implemented layers:

- SQLAlchemy Model
- Pydantic Schemas
- Repository
- Service
- Router

---

## 🔐 Protected Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/profiles` | Create user profile |
| GET | `/profiles/me` | Retrieve current user's profile |
| PUT | `/profiles/me` | Update current user's profile |

Authentication is required using:

```
Authorization: Bearer <Supabase Access Token>
```

---

## 🗄 Database

Database Provider:

- Supabase PostgreSQL

Current Tables:

- profiles

Implemented:

- SQLAlchemy Models
- Relationships ready for expansion
- Row Level Security (RLS)
- Protected profile access

---

## 🖼 Profile Images

Profile images are stored using **Supabase Storage**.

Current implementation:

- Storage bucket
- Storage policies
- Image URL stored inside the `profiles` table

Flow:

```
Flutter
    ↓
Upload Image
    ↓
Supabase Storage
    ↓
Receive Public URL
    ↓
PUT /profiles/me
    ↓
Store URL in PostgreSQL
```

---

## 📌 Current API Flow

```
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
Service Layer
      ↓
Repository Layer
      ↓
Supabase PostgreSQL
```

---

## 🚧 Planned Features

- Pantry Management
- Ingredient Inventory
- AI Meal Recommendation Engine
- Weekly Meal Planner
- Grocery List Generator
- Saved Meals
- Favorites
- Nutrition Information
- Admin Module

---

## ⚙ Installation

Clone the repository.

```bash
git clone https://github.com/<username>/TipidMeal-Backend.git
```

Create a virtual environment.

```bash
python -m venv venv
```

Activate it.

Windows:

```bash
venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env` file.

Example:

```env
DATABASE_URL=your_database_url
SUPABASE_JWT_SECRET=your_jwt_secret
JWT_ALGORITHM=HS256
```

Run the server.

```bash
uvicorn main:app --reload
```

---

## 📖 API Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

## 📄 License

This project is developed as part of an undergraduate thesis.