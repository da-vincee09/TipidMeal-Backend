from __future__ import annotations

import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database.base import Base


class IngredientSubstitution(Base):
    __tablename__ = "ingredient_substitutions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    ingredient: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    substitute: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )