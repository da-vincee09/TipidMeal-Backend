"""seed ingredient substitutions

Revision ID: 80b9d0d7cf89
Revises: acc64e062c88
Create Date: 2026-08-15 17:12:50.191627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

import uuid


# revision identifiers, used by Alembic.
revision: str = '80b9d0d7cf89'
down_revision: Union[str, Sequence[str], None] = 'acc64e062c88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    substitution_table = sa.table(
        "ingredient_substitutions",
        sa.column("id", sa.Uuid()),
        sa.column("ingredient", sa.String(length=100)),
        sa.column("substitute", sa.String(length=100)),
    )

    op.bulk_insert(
        substitution_table,
        [
            {
                "id": uuid.uuid4(),
                "ingredient": "milk",
                "substitute": "evaporated_milk",
            },
            {
                "id": uuid.uuid4(),
                "ingredient": "butter",
                "substitute": "margarine",
            },
            {
                "id": uuid.uuid4(),
                "ingredient": "soy_sauce",
                "substitute": "fish_sauce",
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    substitution_table = sa.table(
        "ingredient_substitutions",
        sa.column("ingredient", sa.String(length=100)),
    )

    op.execute(
        substitution_table.delete().where(
            substitution_table.c.ingredient.in_(
                [
                    "milk",
                    "butter",
                    "soy_sauce",
                ]
            )
        )
    )