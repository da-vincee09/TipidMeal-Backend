"""convert meal_ingredients.ingredient to ingredient_id FK

Revision ID: e3d4f5a6b7c8
Revises: d2d3e4f5a6b7
Create Date: 2026-09-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'e3d4f5a6b7c8'
down_revision = 'd2d3e4f5a6b7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add the new column, nullable for now (populate before enforcing).
    op.add_column(
        'meal_ingredients',
        sa.Column('ingredient_id', postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 2. Backfill: match each existing string value against ingredients.name.
    #    Source data was already normalized to snake_case in the earlier
    #    cleanup pass, so this join should match every row.
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE meal_ingredients
        SET ingredient_id = ingredients.id
        FROM ingredients
        WHERE meal_ingredients.ingredient = ingredients.name
    """))

    # 3. Safety check — fail loudly if anything didn't match, rather than
    #    silently dropping the constraint on unmatched rows.
    unmatched = conn.execute(sa.text(
        "SELECT COUNT(*) FROM meal_ingredients WHERE ingredient_id IS NULL"
    )).scalar()
    if unmatched:
        raise RuntimeError(
            f"{unmatched} meal_ingredients rows failed to match an ingredient "
            f"by name — check for stray values not covered by the earlier "
            f"normalization pass before re-running this migration."
        )

    # 4. Enforce NOT NULL + FK now that every row is populated.
    op.alter_column('meal_ingredients', 'ingredient_id', nullable=False)
    op.create_foreign_key(
        'fk_meal_ingredients_ingredient_id',
        'meal_ingredients', 'ingredients',
        ['ingredient_id'], ['id'],
    )
    op.create_index(
        'ix_meal_ingredients_ingredient_id',
        'meal_ingredients', ['ingredient_id'],
    )

    # 5. Drop the old string column — it's fully replaced now.
    op.drop_column('meal_ingredients', 'ingredient')


def downgrade() -> None:
    op.add_column(
        'meal_ingredients',
        sa.Column('ingredient', sa.String(length=100), nullable=True),
    )
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE meal_ingredients
        SET ingredient = ingredients.name
        FROM ingredients
        WHERE meal_ingredients.ingredient_id = ingredients.id
    """))
    op.alter_column('meal_ingredients', 'ingredient', nullable=False)
    op.drop_index('ix_meal_ingredients_ingredient_id', table_name='meal_ingredients')
    op.drop_constraint('fk_meal_ingredients_ingredient_id', 'meal_ingredients', type_='foreignkey')
    op.drop_column('meal_ingredients', 'ingredient_id')