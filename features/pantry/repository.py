from uuid import UUID
from sqlalchemy.orm import Session
from features.pantry.models.pantry_item import PantryItem
from features.pantry.schemas import (
    PantryItemCreate,
    PantryItemUpdate,
)

def create_pantry_item(
    db: Session,
    profile_id: UUID,
    pantry_data: PantryItemCreate,
) -> PantryItem:


    pantry_item = PantryItem(
        profile_id=profile_id,
        ingredient=pantry_data.ingredient,
        quantity=pantry_data.quantity,
        unit=pantry_data.unit,
    )

    db.add(pantry_item)
    db.commit()
    db.refresh(pantry_item)

    return pantry_item


def get_pantry_items(
    db: Session,
    profile_id: UUID,
) -> list[PantryItem]:


    return (
        db.query(PantryItem)
        .filter(
            PantryItem.profile_id == profile_id
        )
        .all()
    )


def get_pantry_item_by_id(
    db: Session,
    pantry_item_id: UUID,
    profile_id: UUID,
) -> PantryItem | None:


    return (
        db.query(PantryItem)
        .filter(
            PantryItem.id == pantry_item_id,
            PantryItem.profile_id == profile_id,
        )
        .first()
    )


def update_pantry_item(
    db: Session,
    pantry_item: PantryItem,
    pantry_data: PantryItemUpdate,
) -> PantryItem:


    update_data = pantry_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(pantry_item, key, value)

    db.commit()
    db.refresh(pantry_item)

    return pantry_item


def delete_pantry_item(
    db: Session,
    pantry_item: PantryItem,
) -> None:

    db.delete(pantry_item)
    db.commit()

