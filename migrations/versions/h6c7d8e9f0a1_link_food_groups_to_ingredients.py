"""link ingredient_food_groups to ingredients

Replaces the name-based join (ingredient_food_groups.ingredient_name) with a
real foreign key to ingredients.id, and adds food groups for ingredients that
had none.

Revision ID: h6c7d8e9f0a1
Revises: g5b6c7d8e9f0
Create Date: 2026-09-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "h6c7d8e9f0a1"
# Confirm with `alembic heads` before running.
down_revision: Union[str, None] = "g5b6c7d8e9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Ingredients that previously had no food group row.
# Matches existing convention: cheese = grow, cooking_oil = other.
NEW_GROUPS = [
    ("milk", "grow"),
    ("evaporated_milk", "grow"),
    ("butter", "other"),
    ("margarine", "other"),
]


def upgrade() -> None:
    # 1. Add the new column as nullable so existing rows stay valid.
    op.add_column(
        "ingredient_food_groups",
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 2. Backfill by matching names (case/whitespace-insensitive).
    op.execute(
        """
        UPDATE ingredient_food_groups g
        SET ingredient_id = i.id
        FROM ingredients i
        WHERE lower(trim(i.name)) = lower(trim(g.ingredient_name))
        """
    )

    # 3. Add the missing food groups (ingredient_name still exists here).
    for name, group in NEW_GROUPS:
        op.execute(
            f"""
            INSERT INTO ingredient_food_groups
                (id, ingredient_name, ingredient_id, food_group)
            SELECT gen_random_uuid(), i.name, i.id, '{group}'
            FROM ingredients i
            WHERE i.name = '{name}'
              AND NOT EXISTS (
                  SELECT 1 FROM ingredient_food_groups g
                  WHERE g.ingredient_id = i.id
              )
            """
        )

    # 4. Fail loudly instead of silently keeping unmatched rows.
    op.execute(
        """
        DO $$
        DECLARE unmatched integer;
        BEGIN
            SELECT count(*) INTO unmatched
            FROM ingredient_food_groups
            WHERE ingredient_id IS NULL;
            IF unmatched > 0 THEN
                RAISE EXCEPTION
                    '% ingredient_food_groups rows have no matching ingredient',
                    unmatched;
            END IF;
        END $$;
        """
    )

    # 5. Enforce the relationship.
    op.alter_column("ingredient_food_groups", "ingredient_id", nullable=False)
    op.create_foreign_key(
        "fk_ingredient_food_groups_ingredient_id",
        "ingredient_food_groups",
        "ingredients",
        ["ingredient_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_ingredient_food_groups_ingredient_id",
        "ingredient_food_groups",
        ["ingredient_id"],
    )

    # 6. Drop the name column (also drops its unique constraint).
    op.drop_column("ingredient_food_groups", "ingredient_name")


def downgrade() -> None:
    # Remove the rows this migration added.
    names = ", ".join(f"'{name}'" for name, _ in NEW_GROUPS)
    op.execute(
        f"""
        DELETE FROM ingredient_food_groups g
        USING ingredients i
        WHERE g.ingredient_id = i.id AND i.name IN ({names})
        """
    )

    op.add_column(
        "ingredient_food_groups",
        sa.Column("ingredient_name", sa.String(), nullable=True),
    )
    op.execute(
        """
        UPDATE ingredient_food_groups g
        SET ingredient_name = i.name
        FROM ingredients i
        WHERE i.id = g.ingredient_id
        """
    )
    op.alter_column("ingredient_food_groups", "ingredient_name", nullable=False)
    op.create_unique_constraint(
        "ingredient_food_groups_ingredient_name_key",
        "ingredient_food_groups",
        ["ingredient_name"],
    )

    op.drop_constraint(
        "uq_ingredient_food_groups_ingredient_id",
        "ingredient_food_groups",
        type_="unique",
    )
    op.drop_constraint(
        "fk_ingredient_food_groups_ingredient_id",
        "ingredient_food_groups",
        type_="foreignkey",
    )
    op.drop_column("ingredient_food_groups", "ingredient_id")