from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from shared.database.base import Base


if TYPE_CHECKING:
    from features.profiles.models.profile import Profile
    from features.meals.models.meal import Meal


class MealPlanEntry(Base):
    __tablename__ = "meal_plan_entries"

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
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )

    planned_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    meal_slot: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
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
        Index(
            "ix_meal_plan_entries_profile_date",
            "profile_id",
            "planned_date",
        ),
    )

    meal: Mapped["Meal"] = relationship(
        "Meal",
        lazy="joined",
    )