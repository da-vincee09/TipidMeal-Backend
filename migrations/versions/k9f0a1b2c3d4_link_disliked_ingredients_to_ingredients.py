"""link disliked_ingredients to ingredients

Same insert-if-missing pattern as ingredient_substitutions: the
current values come from a hardcoded Flutter checklist, not
necessarily the seeded meal vocabulary, so unmatched names are
created in ingredients rather than causing a failure.

Revision ID: k9f0a1b2c3d4
Revises: j8e9f0a1b2c3
Create Date: 2026-09-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "k9f0a1b2c3d4"
down_revision: Union[str, None] = "j8e9f0a1b2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "disliked_ingredients",
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.execute(
        """
        INSERT INTO ingredients (id, name)
        SELECT gen_random_uuid(), d.name
        FROM (SELECT DISTINCT ingredient AS name FROM disliked_ingredients) AS d
        WHERE NOT EXISTS (
            SELECT 1 FROM ingredients i
            WHERE lower(trim(i.name)) = lower(trim(d.name))
        )
        """
    )

    op.execute(
        """
        UPDATE disliked_ingredients d
        SET ingredient_id = i.id
        FROM ingredients i
        WHERE lower(trim(i.name)) = lower(trim(d.ingredient))
        """
    )

    op.alter_column("disliked_ingredients", "ingredient_id", nullable=False)
    op.create_foreign_key(
        "fk_disliked_ingredients_ingredient_id",
        "disliked_ingredients",
        "ingredients",
        ["ingredient_id"],
        ["id"],
    )

    op.drop_column("disliked_ingredients", "ingredient")


def downgrade() -> None:
    op.add_column(
        "disliked_ingredients",
        sa.Column("ingredient", sa.String(length=100), nullable=True),
    )
    op.execute(
        """
        UPDATE disliked_ingredients d
        SET ingredient = i.name
        FROM ingredients i
        WHERE i.id = d.ingredient_id
        """
    )
    op.alter_column("disliked_ingredients", "ingredient", nullable=False)

    op.drop_constraint(
        "fk_disliked_ingredients_ingredient_id",
        "disliked_ingredients",
        type_="foreignkey",
    )
    op.drop_column("disliked_ingredients", "ingredient_id")