from uuid import UUID
from datetime import date
from decimal import Decimal

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from core.dependencies import get_db
from shared.auth.dependencies import get_current_user

from features.meal_planner import service
from features.meal_planner.schemas import (
    MealPlanEntryCreate,
    MealPlanEntryUpdate,
    MealPlanEntryResponse,
    WeeklyPlanResponse,
)

from features.profiles import service as profile_service


router = APIRouter(
    prefix="/meal-planner",
    tags=["Meal Planner"],
)


@router.post(
    "",
    response_model=MealPlanEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_meal_plan_entry(
    entry_data: MealPlanEntryCreate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return service.create_meal_plan_entry(
        db,
        profile.id,
        entry_data,
    )


@router.get(
    "",
    response_model=WeeklyPlanResponse,
)
def get_meal_plan_entries(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    entries = service.get_meal_plan_entries(
        db,
        profile.id,
        start_date,
        end_date,
    )

    estimated_cost_total = sum(
        (entry.meal.estimated_cost for entry in entries),
        Decimal("0"),
    )

    return {
        "entries": entries,
        "start_date": start_date,
        "end_date": end_date,
        "estimated_cost_total": estimated_cost_total,
    }


@router.get(
    "/{entry_id}",
    response_model=MealPlanEntryResponse,
)
def get_meal_plan_entry(
    entry_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return service.get_meal_plan_entry_by_id(
        db,
        entry_id,
        profile.id,
    )


@router.put(
    "/{entry_id}",
    response_model=MealPlanEntryResponse,
)
def update_meal_plan_entry(
    entry_id: UUID,
    entry_data: MealPlanEntryUpdate,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    entry = service.get_meal_plan_entry_by_id(
        db,
        entry_id,
        profile.id,
    )

    return service.update_meal_plan_entry(
        db,
        entry,
        entry_data,
    )


@router.delete(
    "/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_meal_plan_entry(
    entry_id: UUID,
    current_user: UUID = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = profile_service.get_profile_by_auth_id(
        db,
        current_user,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    entry = service.get_meal_plan_entry_by_id(
        db,
        entry_id,
        profile.id,
    )

    service.delete_meal_plan_entry(
        db,
        entry,
    )

    return None