from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database.base import Base

if TYPE_CHECKING:
    from features.ingredients.models.ingredient import Ingredient


class IngredientFoodGroup(Base):
    __tablename__ = "ingredient_food_groups"
    __table_args__ = (
        UniqueConstraint(
            "ingredient_id",
            name="uq_ingredient_food_groups_ingredient_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # One food group row per ingredient. Names match the migration so
    # Alembic autogenerate sees no drift.
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "ingredients.id",
            ondelete="CASCADE",
            name="fk_ingredient_food_groups_ingredient_id",
        ),
        nullable=False,
    )

    # go | grow | glow | other
    food_group: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    ingredient: Mapped["Ingredient"] = relationship(
        back_populates="food_group_entry",
    )