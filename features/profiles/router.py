from uuid import UUID
from fastapi import APIRouter, Depends, status
from features.profiles import service
from features.profiles.schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate
)
from core.dependencies import get_db, get_current_user
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"],
)


@router.post(
    "", 
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    profile_data: ProfileCreate,
    current_user: UUID = Depends(get_current_user), # later on current_user = Depends(get_current_user)
    db: Session = Depends(get_db),
):
    return service.create_profile(
        db, 
        profile_data, 
        current_user,
    )


@router.get(
    "/me",
    response_model=ProfileResponse,
)
def get_profile(
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_profile(
        db,
        current_user,
    )


@router.put(
    "/me",
    response_model=ProfileResponse,
)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.update_profile(
        db,
        current_user,
        profile_data,
    )



