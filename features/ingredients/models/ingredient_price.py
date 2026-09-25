from __future__ import annotations
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.base import Base
from sqlalchemy.sql import func
from datetime import datetime

if TYPE_CHECKING:
    from .ingredient import Ingredient


class IngredientPrice(Base):
    __tablename__ = "ingredient_prices"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("ingredients.id"),
        nullable=False,
        index=True,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    ingredient: Mapped["Ingredient"] = relationship(
        lazy="joined",
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

    __table_args__ = (
        UniqueConstraint("ingredient_id", "unit", name="uq_ingredient_price_unit"),
    )