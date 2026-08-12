from __future__ import annotations
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from shared.database.base import Base


if TYPE_CHECKING:
    from .meal_ingredient import MealIngredient
    from .meal_instruction import MealInstruction


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    estimated_cost: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    cooking_time: Mapped[int] = mapped_column(
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    servings: Mapped[int] = mapped_column(
        nullable=False,
    )

    calories: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    ingredients: Mapped[list["MealIngredient"]] = relationship(
        back_populates="meal",
        cascade="all, delete-orphan",
    )

    instructions: Mapped[list["MealInstruction"]] = relationship(
        back_populates="meal",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )