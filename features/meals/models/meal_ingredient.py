from __future__ import annotations
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.base import Base


if TYPE_CHECKING:
    from .meal import Meal


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

    ingredient: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
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