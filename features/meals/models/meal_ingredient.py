from __future__ import annotations
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.base import Base


if TYPE_CHECKING:
    from .meal import Meal
    from features.ingredients.models.ingredient import Ingredient


class MealIngredient(Base):
    __tablename__ = "meal_ingredients"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    meal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("meals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ingredients.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_optional: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    meal: Mapped["Meal"] = relationship(
        back_populates="ingredients",
    )

    ingredient_ref: Mapped["Ingredient"] = relationship(
        lazy="joined",  # avoids N+1 queries — every place reading .ingredient
                         # (the property below) needs this loaded anyway
    )

    @property
    def ingredient(self) -> str:
        """
        Compatibility shim: every existing call site across recommendations,
        nutrition, and grocery_list reads `.ingredient` expecting a plain
        string. This property preserves that contract while the actual
        storage is now normalized via ingredient_id -> Ingredient.name.
        """
        return self.ingredient_ref.name