"""create ingredient_prices table

Revision ID: g5b6c7d8e9f0
Revises: f4a5b6c7d8e9
Create Date: 2026-09-21

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'g5b6c7d8e9f0'
down_revision = 'f4a5b6c7d8e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'ingredient_prices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('ingredient_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('price_per_unit', sa.Numeric(10, 2), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id']),
        sa.UniqueConstraint('ingredient_id', 'unit', name='uq_ingredient_price_unit'),
    )
    op.create_index('ix_ingredient_prices_ingredient_id', 'ingredient_prices', ['ingredient_id'])


def downgrade() -> None:
    op.drop_index('ix_ingredient_prices_ingredient_id', table_name='ingredient_prices')
    op.drop_table('ingredient_prices')