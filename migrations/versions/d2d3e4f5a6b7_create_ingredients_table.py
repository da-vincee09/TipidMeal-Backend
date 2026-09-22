"""create ingredients table and backfill from existing sources

Revision ID: d2d3e4f5a6b7
Revises: c7d8e9f0a1b2
Create Date: 2026-09-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'd2d3e4f5a6b7'
down_revision = 'c7d8e9f0a1b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.UniqueConstraint('name', name='uq_ingredients_name'),
    )
    op.create_index('ix_ingredients_name', 'ingredients', ['name'])

    conn = op.get_bind()

    sources = [
        ("meal_ingredients", "ingredient"),
        ("pantry_items", "ingredient"),
        ("ingredient_substitutions", "ingredient"),
        ("ingredient_substitutions", "substitute"),
        ("ingredient_food_groups", "ingredient_name"),
    ]

    distinct_names: set[str] = set()

    for table, column in sources:
        result = conn.execute(
            sa.text(f"SELECT DISTINCT {column} FROM {table} WHERE {column} IS NOT NULL")
        )
        for row in result:
            name = row[0]
            if name and name.strip():
                distinct_names.add(name.strip().lower())

    if distinct_names:
        ingredients_table = sa.table(
            'ingredients',
            sa.column('id', postgresql.UUID(as_uuid=True)),
            sa.column('name', sa.String),
        )
        conn.execute(
            ingredients_table.insert(),
            [{"id": uuid.uuid4(), "name": name} for name in sorted(distinct_names)],
        )


def downgrade() -> None:
    op.drop_index('ix_ingredients_name', table_name='ingredients')
    op.drop_table('ingredients')