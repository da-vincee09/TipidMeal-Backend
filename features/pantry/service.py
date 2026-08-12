from uuid import UUID
from sqlalchemy.orm import Session
from features.pantry.schemas import (
    PantryItemCreate,
    PantryItemUpdate,
)
from features.pantry.models.pantry_item import PantryItem
from features.pantry import repository


def create_pantry_item(
    db: Session,
    profile_id: UUID,
    pantry_data: PantryItemCreate
) -> PantryItem:

    return repository.create_pantry_item(
        db,
        profile_id,
        pantry_data,
    )


def get_pantry_items(
    db: Session,
    profile_id: UUID
) -> list[PantryItem]:

    return repository.get_pantry_items(
        db,
        profile_id,
    )


def get_pantry_item_by_id(
    db: Session,
    pantry_item_id: UUID,
    profile_id: UUID
) -> PantryItem | None:

    return repository.get_pantry_item_by_id(
        db,
        pantry_item_id,
        profile_id,
    )


def update_pantry_item(
    db: Session,
    pantry_item: PantryItem,
    pantry_data: PantryItemUpdate
) -> PantryItem:

    return repository.update_pantry_item(
        db,
        pantry_item,
        pantry_data,
    )


def delete_pantry_item(
    db: Session,
    pantry_item: PantryItem
) -> None:

    repository.delete_pantry_item(
        db,
        pantry_item,
    )

