from fastapi import APIRouter

from features.profiles.router import router as profile_router


api_router = APIRouter()


api_router.include_router(
    profile_router,
)