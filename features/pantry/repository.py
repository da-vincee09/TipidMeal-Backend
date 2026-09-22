from uuid import UUID
from sqlalchemy.orm import Session
from features.pantry.models.pantry_item import PantryItem
from features.pantry.schemas import (
    PantryItemCreate,
    PantryItemUpdate,
)
from features.ingredients.repository import get_or_create_ingredient


def create_pantry_item(
    db: Session,
    profile_id: UUID,
    pantry_data: PantryItemCreate,
) -> PantryItem:

    ingredient_row = get_or_create_ingredient(db, pantry_data.ingredient)

    pantry_item = PantryItem(
        profile_id=profile_id,
        ingredient_id=ingredient_row.id,
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

    # "ingredient" needs special handling — it's a read-only property
    # now (backed by ingredient_id), so the generic setattr loop below
    # would raise AttributeError if we let it try. Resolve to an
    # Ingredient row and set ingredient_id directly instead.
    if "ingredient" in update_data:
        ingredient_name = update_data.pop("ingredient")
        ingredient_row = get_or_create_ingredient(db, ingredient_name)
        pantry_item.ingredient_id = ingredient_row.id

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