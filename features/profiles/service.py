from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from features.profiles import repository
from features.profiles.schemas import (
    ProfileCreate,
    ProfileUpdate,
)

def create_profile(
    db: Session,
    profile_data: ProfileCreate,
    auth_id: UUID
): 
    existing_profile = repository.get_profile_by_auth_id(
        db, auth_id,
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists!",
        )

    return repository.create_profile(
        db,
        profile_data,
        auth_id,
    )

def get_profile(
    db: Session,
    auth_id: UUID
):
    profile = repository.get_profile_by_auth_id(db, auth_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return profile

def update_profile(
    db: Session,
    auth_id: UUID,
    profile_data: ProfileUpdate,
):
    profile = repository.get_profile_by_auth_id(db, auth_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return repository.update_profile(
        db,
        profile,
        profile_data
    )
    
