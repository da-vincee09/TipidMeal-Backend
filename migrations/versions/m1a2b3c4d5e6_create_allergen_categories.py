"""create allergen_categories table and seed placeholder mappings

Revision ID: m1a2b3c4d5e6
Revises: l0a1b2c3d4e5
Create Date: 2026-09-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

revision = 'm1a2b3c4d5e6'
down_revision = 'l0a1b2c3d4e5'
branch_labels = None
depends_on = None


# PLACEHOLDER mapping — category -> ingredient names (must already exist
# in `ingredients`). Judgment calls made here (fish_sauce/bagoong under
# Fish/Shellfish, margarine and coconut_milk excluded from Milk/Dairy)
# should be reviewed before this is treated as authoritative. Peanuts,
# Tree Nuts, and Sesame have no matches in the current ~68-ingredient
# seed vocabulary.
ALLERGEN_MAPPING = {
    "Shellfish": ["shrimp", "shrimp_paste", "bagoong"],
    "Shrimp": ["shrimp", "shrimp_paste", "bagoong"],
    "Fish": ["fish_sauce", "canned_sardines"],
    "Eggs": ["egg", "quail_egg"],
    "Milk/Dairy": ["milk", "evaporated_milk", "cheese", "butter"],
    "Soy": ["soy_sauce"],
    "Wheat/Gluten": ["flour", "lumpia_wrappers"],
}


def upgrade() -> None:
    op.create_table(
        'allergen_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('ingredient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id']),
        sa.UniqueConstraint('category', 'ingredient_id', name='uq_allergen_category_ingredient'),
    )
    op.create_index('ix_allergen_categories_category', 'allergen_categories', ['category'])
    op.create_index('ix_allergen_categories_ingredient_id', 'allergen_categories', ['ingredient_id'])

    conn = op.get_bind()

    for category, ingredient_names in ALLERGEN_MAPPING.items():
        for name in ingredient_names:
            row = conn.execute(
                sa.text("SELECT id FROM ingredients WHERE name = :name"),
                {"name": name},
            ).fetchone()

            if row is None:
                print(f"WARNING: ingredient '{name}' not found in ingredients table — skipping ({category})")
                continue

            conn.execute(
                sa.text(
                    "INSERT INTO allergen_categories (id, category, ingredient_id) "
                    "VALUES (:id, :category, :ingredient_id)"
                ),
                {"id": str(uuid.uuid4()), "category": category, "ingredient_id": row[0]},
            )


def downgrade() -> None:
    op.drop_index('ix_allergen_categories_ingredient_id', table_name='allergen_categories')
    op.drop_index('ix_allergen_categories_category', table_name='allergen_categories')
    op.drop_table('allergen_categories')