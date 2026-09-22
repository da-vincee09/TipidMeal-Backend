"""convert pantry_items.ingredient to ingredient_id FK

Revision ID: f4a5b6c7d8e9
Revises: e3d4f5a6b7c8
Create Date: 2026-09-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'f4a5b6c7d8e9'
down_revision = 'e3d4f5a6b7c8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'pantry_items',
        sa.Column('ingredient_id', postgresql.UUID(as_uuid=True), nullable=True),
    )

    conn = op.get_bind()

    # Normalize any pantry ingredient strings the same way meal_ingredients
    # was normalized in the earlier cleanup pass, in case a user entered
    # something with different spacing/casing that never got touched
    # (pantry entries are user-submitted, not seed data, so this is a
    # real possibility meal_ingredients didn't have).
    conn.execute(sa.text("""
        UPDATE pantry_items
        SET ingredient = REPLACE(TRIM(LOWER(ingredient)), ' ', '_')
    """))

    conn.execute(sa.text("""
        UPDATE pantry_items
        SET ingredient_id = ingredients.id
        FROM ingredients
        WHERE pantry_items.ingredient = ingredients.name
    """))

    # Any pantry ingredient with no match gets auto-created as a new
    # Ingredient row, rather than failing the migration — unlike seeded
    # meal data, user-entered pantry items may reference ingredients
    # that genuinely don't exist in the ingredients table yet.
    unmatched = conn.execute(sa.text(
        "SELECT DISTINCT ingredient FROM pantry_items WHERE ingredient_id IS NULL"
    )).fetchall()

    if unmatched:
        import uuid
        for row in unmatched:
            name = row[0]
            new_id = str(uuid.uuid4())
            conn.execute(
                sa.text("INSERT INTO ingredients (id, name) VALUES (:id, :name)"),
                {"id": new_id, "name": name},
            )
            conn.execute(
                sa.text("UPDATE pantry_items SET ingredient_id = :id WHERE ingredient = :name"),
                {"id": new_id, "name": name},
            )
        print(f"Created {len(unmatched)} new ingredient(s) from pantry data not in seed set: "
              f"{[r[0] for r in unmatched]}")

    op.alter_column('pantry_items', 'ingredient_id', nullable=False)
    op.create_foreign_key(
        'fk_pantry_items_ingredient_id',
        'pantry_items', 'ingredients',
        ['ingredient_id'], ['id'],
    )
    op.create_index(
        'ix_pantry_items_ingredient_id',
        'pantry_items', ['ingredient_id'],
    )

    op.drop_column('pantry_items', 'ingredient')


def downgrade() -> None:
    op.add_column(
        'pantry_items',
        sa.Column('ingredient', sa.String(length=100), nullable=True),
    )
    conn = op.get_bind()
    conn.execute(sa.text("""
        UPDATE pantry_items
        SET ingredient = ingredients.name
        FROM ingredients
        WHERE pantry_items.ingredient_id = ingredients.id
    """))
    op.alter_column('pantry_items', 'ingredient', nullable=False)
    op.drop_index('ix_pantry_items_ingredient_id', table_name='pantry_items')
    op.drop_constraint('fk_pantry_items_ingredient_id', 'pantry_items', type_='foreignkey')
    op.drop_column('pantry_items', 'ingredient_id')