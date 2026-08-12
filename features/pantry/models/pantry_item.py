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

    ingredient: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
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

    created_at: Mapped[DateTime] = mapped_column( 
        DateTime(timezone=True), 
        server_default=func.now(), 
    )

    updated_at: Mapped[DateTime] = mapped_column( 
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
    )