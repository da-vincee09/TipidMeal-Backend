from fastapi import APIRouter

from features.profiles.router import router as profile_router
from features.pantry.router import router as pantry_router
from features.meals.router import router as meal_router

api_router = APIRouter()


api_router.include_router(
    profile_router,
)

api_router.include_router(
    pantry_router,
)

api_router.include_router(
    meal_router,
)