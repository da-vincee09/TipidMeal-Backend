"""rename daily_budget to budget_per_meal on profiles

Revision ID: c7d8e9f0a1b2
Revises: c2d3e4f5a6b7
Create Date: 2026-09-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c7d8e9f0a1b2'
down_revision: Union[str, Sequence[str], None] = 'c2d3e4f5a6b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'profiles',
        'daily_budget',
        new_column_name='budget_per_meal',
    )


def downgrade() -> None:
    op.alter_column(
        'profiles',
        'budget_per_meal',
        new_column_name='daily_budget',
    )