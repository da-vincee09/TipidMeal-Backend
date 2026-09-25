"""merge pc into pcs, create unit_conversions table

Revision ID: n2b3c4d5e6f7
Revises: m1a2b3c4d5e6
Create Date: 2026-09-22

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

revision = 'n2b3c4d5e6f7'
down_revision = 'm1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Merge 'pc' into 'pcs' everywhere units are stored.
    for table in ("meal_ingredients", "pantry_items", "ingredient_prices"):
        conn.execute(sa.text(f"UPDATE {table} SET unit = 'pcs' WHERE unit = 'pc'"))

    # 2. Create unit_conversions table.
    op.create_table(
        'unit_conversions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('from_unit', sa.String(length=20), nullable=False),
        sa.Column('to_unit', sa.String(length=20), nullable=False),
        sa.Column('factor', sa.Numeric(18, 6), nullable=False),
        sa.UniqueConstraint('from_unit', 'to_unit', name='uq_unit_conversion_pair'),
    )

    # 3. Seed canonical conversions. Weight -> g, Volume -> ml.
    #    Count units (pcs, cloves) intentionally excluded — no reliable
    #    universal conversion without per-ingredient weight assumptions.
    conversions = [
        ("kg", "g", "1000"),
        ("g", "kg", "0.001"),
        ("l", "ml", "1000"),
        ("ml", "l", "0.001"),
        ("cup", "ml", "240"),
        ("ml", "cup", "0.0041667"),
        ("tbsp", "ml", "15"),
        ("ml", "tbsp", "0.0666667"),
        ("tsp", "ml", "5"),
        ("ml", "tsp", "0.2"),
    ]

    conv_table = sa.table(
        'unit_conversions',
        sa.column('id', postgresql.UUID(as_uuid=True)),
        sa.column('from_unit', sa.String),
        sa.column('to_unit', sa.String),
        sa.column('factor', sa.Numeric),
    )

    conn.execute(
        conv_table.insert(),
        [
            {"id": str(uuid.uuid4()), "from_unit": f, "to_unit": t, "factor": factor}
            for f, t, factor in conversions
        ],
    )


def downgrade() -> None:
    op.drop_table('unit_conversions')