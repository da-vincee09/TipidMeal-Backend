from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from shared.storage.supabase_storage import upload_profile_image, StorageUploadError
from features.profiles import service
from features.profiles.schemas import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate
)
from core.dependencies import get_db
from shared.auth.dependencies import get_current_user
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
    current_user: UUID = Depends(get_current_user), 
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
    profile = service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    return profile


@router.put(
    "/me",
    response_model=ProfileResponse,
)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:

        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    return service.update_profile(
        db,
        profile,
        profile_data,
    )


@router.post("/me/image")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = service.get_profile_by_auth_id(db, current_user)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    file_bytes = await file.read()

    try:
        public_url = upload_profile_image(
            file_bytes=file_bytes,
            content_type=file.content_type,
            auth_id=current_user,
        )
    except StorageUploadError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    profile.profile_image_url = public_url
    db.commit()
    db.refresh(profile)

    return {"profile_image_url": public_url}



