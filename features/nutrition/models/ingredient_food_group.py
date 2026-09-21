from __future__ import annotations
import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from shared.database.base import Base


class IngredientFoodGroup(Base):
    __tablename__ = "ingredient_food_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Matches the existing free-text ingredient vocabulary used by
    # meal_ingredients / pantry_items — not a foreign key, since
    # ingredient names aren't a separate normalized table elsewhere
    # in the app either.
    ingredient_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    # go | grow | glow | other
    food_group: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )