"""link ingredient_substitutions to ingredients

Replaces the two free-text columns (ingredient, substitute) with real
foreign keys to ingredients.id. Any name not already present in
ingredients is created first (insert-if-missing) rather than failing
the migration, since these values didn't necessarily originate from
the seeded meal vocabulary.

Revision ID: j8e9f0a1b2c3
Revises: i7d8e9f0a1b2
Create Date: 2026-09-22
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "j8e9f0a1b2c3"
down_revision: Union[str, None] = "i7d8e9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the new FK columns as nullable so existing rows stay valid
    #    while we backfill.
    op.add_column(
        "ingredient_substitutions",
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "ingredient_substitutions",
        sa.Column("substitute_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 2. Insert-if-missing: create an Ingredient row for any name used
    #    here that doesn't already exist (case/whitespace-insensitive
    #    match), covering both the "ingredient" and "substitute" sides.
    op.execute(
        """
        INSERT INTO ingredients (id, name)
        SELECT gen_random_uuid(), names.name
        FROM (
            SELECT DISTINCT ingredient AS name FROM ingredient_substitutions
            UNION
            SELECT DISTINCT substitute AS name FROM ingredient_substitutions
        ) AS names
        WHERE NOT EXISTS (
            SELECT 1 FROM ingredients i
            WHERE lower(trim(i.name)) = lower(trim(names.name))
        )
        """
    )

    # 3. Backfill both FK columns by matching names.
    op.execute(
        """
        UPDATE ingredient_substitutions s
        SET ingredient_id = i.id
        FROM ingredients i
        WHERE lower(trim(i.name)) = lower(trim(s.ingredient))
        """
    )
    op.execute(
        """
        UPDATE ingredient_substitutions s
        SET substitute_id = i.id
        FROM ingredients i
        WHERE lower(trim(i.name)) = lower(trim(s.substitute))
        """
    )

    # 4. Enforce the relationship now that every row is backfilled.
    op.alter_column("ingredient_substitutions", "ingredient_id", nullable=False)
    op.alter_column("ingredient_substitutions", "substitute_id", nullable=False)

    op.create_foreign_key(
        "fk_ingredient_substitutions_ingredient_id",
        "ingredient_substitutions",
        "ingredients",
        ["ingredient_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_ingredient_substitutions_substitute_id",
        "ingredient_substitutions",
        "ingredients",
        ["substitute_id"],
        ["id"],
    )

    # Preserve the original "one substitution rule per ingredient"
    # constraint (was a unique index on the old `ingredient` string
    # column), now on ingredient_id.
    op.create_unique_constraint(
        "uq_ingredient_substitutions_ingredient_id",
        "ingredient_substitutions",
        ["ingredient_id"],
    )

    # 5. Drop the old string columns (and the old unique constraint
    #    that lived on `ingredient`, dropped automatically with it).
    op.drop_column("ingredient_substitutions", "ingredient")
    op.drop_column("ingredient_substitutions", "substitute")


def downgrade() -> None:
    op.add_column(
        "ingredient_substitutions",
        sa.Column("ingredient", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "ingredient_substitutions",
        sa.Column("substitute", sa.String(length=100), nullable=True),
    )

    op.execute(
        """
        UPDATE ingredient_substitutions s
        SET ingredient = i.name
        FROM ingredients i
        WHERE i.id = s.ingredient_id
        """
    )
    op.execute(
        """
        UPDATE ingredient_substitutions s
        SET substitute = i.name
        FROM ingredients i
        WHERE i.id = s.substitute_id
        """
    )

    op.alter_column("ingredient_substitutions", "ingredient", nullable=False)
    op.alter_column("ingredient_substitutions", "substitute", nullable=False)
    op.create_unique_constraint(
        "ingredient_substitutions_ingredient_key",
        "ingredient_substitutions",
        ["ingredient"],
    )

    op.drop_constraint(
        "uq_ingredient_substitutions_ingredient_id",
        "ingredient_substitutions",
        type_="unique",
    )
    op.drop_constraint(
        "fk_ingredient_substitutions_substitute_id",
        "ingredient_substitutions",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_ingredient_substitutions_ingredient_id",
        "ingredient_substitutions",
        type_="foreignkey",
    )
    op.drop_column("ingredient_substitutions", "substitute_id")
    op.drop_column("ingredient_substitutions", "ingredient_id")