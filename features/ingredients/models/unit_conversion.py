from __future__ import annotations
import uuid
from decimal import Decimal
from sqlalchemy import String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from shared.database.base import Base


class UnitConversion(Base):
    __tablename__ = "unit_conversions"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    from_unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    to_unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    factor: Mapped[Decimal] = mapped_column(
        Numeric(18, 6),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("from_unit", "to_unit", name="uq_unit_conversion_pair"),
    )