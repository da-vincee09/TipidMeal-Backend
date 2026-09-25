from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database.base import Base

if TYPE_CHECKING:
    from features.ingredients.models.ingredient import Ingredient


class IngredientSubstitution(Base):
    __tablename__ = "ingredient_substitutions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ingredients.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    substitute_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ingredients.id"),
        nullable=False,
    )

    ingredient_ref: Mapped["Ingredient"] = relationship(
        foreign_keys=[ingredient_id],
        lazy="joined",
    )

    substitute_ref: Mapped["Ingredient"] = relationship(
        foreign_keys=[substitute_id],
        lazy="joined",
    )

    @property
    def ingredient(self) -> str:
        """Compatibility shim — same pattern as MealIngredient/PantryItem."""
        return self.ingredient_ref.name

    @property
    def substitute(self) -> str:
        """Compatibility shim — same pattern as MealIngredient/PantryItem."""
        return self.substitute_ref.name