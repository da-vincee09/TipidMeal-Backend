from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from shared.database.base import Base
from decimal import Decimal

if TYPE_CHECKING:
    from ...profiles.models.profile import Profile
    from features.ingredients.models.ingredient import Ingredient

class PantryItem(Base):
    __tablename__="pantry_items"

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

    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10,2),
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    profile: Mapped["Profile"] = relationship(
        back_populates="pantry_items"
    )

    ingredient_ref: Mapped["Ingredient"] = relationship(
        lazy="joined",
    )

    created_at: Mapped[DateTime] = mapped_column( 
        DateTime(timezone=True), 
        server_default=func.now(), 
    )

    updated_at: Mapped[DateTime] = mapped_column( 
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
    )

    @property
    def ingredient(self) -> str:
        """
        Compatibility shim — recommendations/service.py's
        get_available_ingredients() reads .ingredient expecting a plain
        string. Read-only: updates to ingredient go through
        repository.update_pantry_item()'s explicit handling, not
        generic setattr (see that function for why).
        """
        return self.ingredient_ref.name