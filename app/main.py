from fastapi import FastAPI
from sqlalchemy import text
from core.config import settings
from core.database import SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from core.exceptions import register_exception_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)

register_exception_handlers(app)

