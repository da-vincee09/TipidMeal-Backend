from uuid import UUID
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from features.pantry import service
from features.pantry.schemas import (
    PantryItemCreate,
    PantryItemResponse,
    PantryItemUpdate,
)
from features.profiles import service as profile_service
from core.dependencies import get_db
from shared.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/pantry",
    tags=["Pantry"],
)


@router.post(
    "",
    response_model=PantryItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_pantry_item(
    pantry_data: PantryItemCreate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    return service.create_pantry_item(
        db,
        profile.id,
        pantry_data,
    )


@router.get(
    "",
    response_model=list[PantryItemResponse],
)
def get_pantry_items(
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    return service.get_pantry_items(
        db,
        profile.id,
    )


@router.get(
    "/{pantry_item_id}",
    response_model=PantryItemResponse,
)
def get_pantry_item(
    pantry_item_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    pantry_item = service.get_pantry_item_by_id(
        db,
        pantry_item_id,
        profile.id,
    )

    if pantry_item is None:
        raise HTTPException(
            status_code=404,
            detail="Pantry item not found",
        )

    return pantry_item


@router.put(
    "/{pantry_item_id}",
    response_model=PantryItemResponse,
)
def update_pantry_item(
    pantry_item_id: UUID,
    pantry_data: PantryItemUpdate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    pantry_item = service.get_pantry_item_by_id(
        db,
        pantry_item_id,
        profile.id,
    )

    if pantry_item is None:
        raise HTTPException(
            status_code=404,
            detail="Pantry item not found",
        )

    return service.update_pantry_item(
        db,
        pantry_item,
        pantry_data,
    )


@router.delete(
    "/{pantry_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pantry_item(
    pantry_item_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )

    pantry_item = service.get_pantry_item_by_id(
        db,
        pantry_item_id,
        profile.id,
    )

    if pantry_item is None:
        raise HTTPException(
            status_code=404,
            detail="Pantry item not found",
        )

    service.delete_pantry_item(
        db,
        pantry_item,
    )

    return None

