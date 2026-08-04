import uuid
from sqlalchemy import String, Integer, Numeric, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from shared.database.base import Base

class Profile(Base):
    __tablename__="profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
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

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    sex: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    daily_budget: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    cooking_skill_level: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    food_allergies: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    disliked_ingredients: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
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

