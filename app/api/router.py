from fastapi import APIRouter

from features.profiles.router import router as profile_router
from features.pantry.router import router as pantry_router
from features.meals.router import router as meal_router
from features.recommendations.router import router as recommendation_router
from features.meal_planner.router import router as meal_planner_router
from features.grocery_list.router import router as grocery_list_router
from features.favorites.router import router as favorites_router


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

api_router.include_router(
    recommendation_router,
)

api_router.include_router(
    meal_planner_router,
)

api_router.include_router(
    grocery_list_router,
)

api_router.include_router(
    favorites_router,
)