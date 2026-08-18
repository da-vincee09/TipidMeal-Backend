from uuid import UUID
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from features.meal_planner import repository
from features.meal_planner.models.meal_plan_entry import MealPlanEntry
from features.meal_planner.schemas import (
    MealPlanEntryCreate,
    MealPlanEntryUpdate,
)
from features.meals import service as meal_service


def create_meal_plan_entry(
    db: Session,
    profile_id: UUID,
    entry_data: MealPlanEntryCreate,
) -> MealPlanEntry:

    meal = meal_service.get_meal_by_id(
        db,
        entry_data.meal_id,
    )

    if meal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )

    return repository.create_meal_plan_entry(
        db,
        profile_id,
        entry_data.meal_id,
        entry_data.planned_date,
        entry_data.meal_slot,
    )


def get_meal_plan_entries(
    db: Session,
    profile_id: UUID,
    start_date: date,
    end_date: date,
) -> list[MealPlanEntry]:

    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before or equal to end_date",
        )

    return repository.get_meal_plan_entries(
        db,
        profile_id,
        start_date,
        end_date,
    )


def get_meal_plan_entry_by_id(
    db: Session,
    entry_id: UUID,
    profile_id: UUID,
) -> MealPlanEntry:

    entry = repository.get_meal_plan_entry_by_id(
        db,
        entry_id,
        profile_id,
    )

    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan entry not found",
        )

    return entry


def update_meal_plan_entry(
    db: Session,
    entry: MealPlanEntry,
    entry_data: MealPlanEntryUpdate,
) -> MealPlanEntry:

    update_data = entry_data.model_dump(
        exclude_unset=True,
    )

    if "meal_id" in update_data:
        meal = meal_service.get_meal_by_id(
            db,
            update_data["meal_id"],
        )

        if meal is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal not found",
            )

    meal_id = update_data.get("meal_id")
    planned_date = update_data.get("planned_date")
    meal_slot = update_data.get("meal_slot")

    return repository.update_meal_plan_entry(
        db,
        entry,
        meal_id,
        planned_date,
        meal_slot,
    )


def delete_meal_plan_entry(
    db: Session,
    entry: MealPlanEntry,
) -> None:

    repository.delete_meal_plan_entry(
        db,
        entry,
    )