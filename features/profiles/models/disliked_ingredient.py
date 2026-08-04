from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from shared.database.base import Base

if TYPE_CHECKING:
    from .profile import Profile


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

    ingredient: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    profile: Mapped["Profile"] = relationship(
        back_populates="disliked_ingredients",
    )