from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.base import Base

if TYPE_CHECKING:
    from .profile import Profile
    from features.ingredients.models.ingredient import Ingredient


class DislikedIngredient(Base):
    __tablename__ = "disliked_ingredients"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ingredients.id"),
        nullable=False,
        index=True,
    )

    profile: Mapped["Profile"] = relationship(
        back_populates="disliked_ingredients",
    )

    ingredient_ref: Mapped["Ingredient"] = relationship(
        lazy="joined",
    )

    @property
    def ingredient(self) -> str:
        """
        Compatibility shim — recommendations/service.py and the
        DislikedIngredientResponse schema both read .ingredient
        expecting a plain string.
        """
        return self.ingredient_ref.name