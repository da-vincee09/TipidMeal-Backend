"""add physical_activity_level to profiles

Revision ID: aa4a5f458607
Revises: 2e7b4adc1b5d
Create Date: 2026-09-20 15:54:05.690996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa4a5f458607'
down_revision: Union[str, Sequence[str], None] = '2e7b4adc1b5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'profiles',
        sa.Column('physical_activity_level', sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('profiles', 'physical_activity_level')
