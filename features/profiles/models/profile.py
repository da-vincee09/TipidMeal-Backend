from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import String, Numeric, Text, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from shared.database.base import Base
from datetime import date
from enum import Enum

if TYPE_CHECKING:
    from .food_allergy import FoodAllergy

if TYPE_CHECKING:
    from .disliked_ingredient import DislikedIngredient

if TYPE_CHECKING:
     from ...pantry.models.pantry_item import PantryItem


class CookingSkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class PhysicalActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    MODERATELY_ACTIVE = "moderately_active"
    ACTIVE = "active"


class Profile(Base):
    __tablename__="profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    auth_id: Mapped[uuid.UUID] = mapped_column(
        unique=True,
        nullable=False,
        index=True,
    )

    profile_image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )   

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    date_of_birth: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    sex: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    budget_per_meal: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    cooking_skill_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    physical_activity_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    food_allergies: Mapped[list["FoodAllergy"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    disliked_ingredients: Mapped[list["DislikedIngredient"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    pantry_items: Mapped[list["PantryItem"]] = relationship(
        back_populates="profile",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

