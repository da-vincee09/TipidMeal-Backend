from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.base import Base

if TYPE_CHECKING:
    from .profile import Profile

class FoodAllergy(Base):
    __tablename__ = "food_allergies"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    allergy: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    profile: Mapped["Profile"] = relationship(
        back_populates="food_allergies",
    )