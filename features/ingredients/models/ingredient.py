from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database.base import Base

if TYPE_CHECKING:
    from features.nutrition.models.ingredient_food_group import (
        IngredientFoodGroup,
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    # At most one food group row per ingredient (go | grow | glow | other).
    food_group_entry: Mapped["IngredientFoodGroup | None"] = relationship(
        back_populates="ingredient",
        uselist=False,
        passive_deletes=True,
    )