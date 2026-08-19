from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from shared.database.base import Base


if TYPE_CHECKING:
    from features.profiles.models.profile import Profile
    from features.meals.models.meal import Meal


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "profiles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    meal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "meals.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    meal: Mapped["Meal"] = relationship(
        "Meal",
        lazy="joined",
    )

    __table_args__ = (
        UniqueConstraint(
            "profile_id",
            "meal_id",
            name="uq_favorites_profile_meal",
        ),
    )