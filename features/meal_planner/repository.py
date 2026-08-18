from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session, joinedload
from features.meal_planner.models.meal_plan_entry import MealPlanEntry
from features.meals.models.meal import Meal


def create_meal_plan_entry(
    db: Session,
    profile_id: UUID,
    meal_id: UUID,
    planned_date: date,
    meal_slot: str | None,
) -> MealPlanEntry:

    entry = MealPlanEntry(
        profile_id=profile_id,
        meal_id=meal_id,
        planned_date=planned_date,
        meal_slot=meal_slot,
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return entry


def get_meal_plan_entries(
    db: Session,
    profile_id: UUID,
    start_date: date,
    end_date: date,
) -> list[MealPlanEntry]:

    return (
        db.query(MealPlanEntry)
        .options(
            joinedload(
                MealPlanEntry.meal
            ).joinedload(
                Meal.ingredients
            )
        )
        .filter(
            MealPlanEntry.profile_id == profile_id,
            MealPlanEntry.planned_date >= start_date,
            MealPlanEntry.planned_date <= end_date,
        )
        .order_by(
            MealPlanEntry.planned_date,
            MealPlanEntry.meal_slot,
        )
        .all()
    )


def get_meal_plan_entry_by_id(
    db: Session,
    entry_id: UUID,
    profile_id: UUID,
) -> MealPlanEntry | None:

    return (
        db.query(MealPlanEntry)
        .filter(
            MealPlanEntry.id == entry_id,
            MealPlanEntry.profile_id == profile_id,
        )
        .first()
    )


def update_meal_plan_entry(
    db: Session,
    entry: MealPlanEntry,
    meal_id: UUID | None,
    planned_date: date | None,
    meal_slot: str | None,
) -> MealPlanEntry:

    if meal_id is not None:
        entry.meal_id = meal_id

    if planned_date is not None:
        entry.planned_date = planned_date

    if meal_slot is not None:
        entry.meal_slot = meal_slot

    db.commit()
    db.refresh(entry)

    return entry


def delete_meal_plan_entry(
    db: Session,
    entry: MealPlanEntry,
) -> None:

    db.delete(entry)
    db.commit()