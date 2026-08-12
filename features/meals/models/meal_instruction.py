from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.base import Base


if TYPE_CHECKING:
    from .meal import Meal


class MealInstruction(Base):
    __tablename__ = "meal_instructions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    meal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("meals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_number: Mapped[int] = mapped_column(
        nullable=False,
    )

    instruction: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    meal: Mapped["Meal"] = relationship(
        back_populates="instructions",
    )