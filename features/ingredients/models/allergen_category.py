from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.base import Base

if TYPE_CHECKING:
    from .ingredient import Ingredient


class AllergenCategory(Base):
    __tablename__ = "allergen_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ingredients.id"),
        nullable=False,
        index=True,
    )

    ingredient: Mapped["Ingredient"] = relationship(
        lazy="joined",
    )

    __table_args__ = (
        UniqueConstraint("category", "ingredient_id", name="uq_allergen_category_ingredient"),
    )