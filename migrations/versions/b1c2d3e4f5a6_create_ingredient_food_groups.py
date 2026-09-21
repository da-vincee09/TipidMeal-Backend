"""create ingredient_food_groups

Revision ID: b1c2d3e4f5a6
Revises: aa4a5f458607
Create Date: 2026-09-21 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'aa4a5f458607'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ingredient_food_groups',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('ingredient_name', sa.String(length=100), nullable=False),
        sa.Column('food_group', sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ingredient_name'),
    )
    op.create_index(
        op.f('ix_ingredient_food_groups_ingredient_name'),
        'ingredient_food_groups',
        ['ingredient_name'],
        unique=True,
    )

    # Seed data — classification per the Week 8 Part 2 discussion.
    # Names are lowercase to match the normalize_ingredient() pattern
    # already used in features/recommendations/utils.py.
    seed_rows = [
        # go
        ('cooked rice', 'go'),
        ('flour', 'go'),
        ('lumpia wrappers', 'go'),

        # grow
        ('beef', 'grow'),
        ('beef sirloin', 'grow'),
        ('chicken', 'grow'),
        ('chicken thighs', 'grow'),
        ('ground pork', 'grow'),
        ('egg', 'grow'),
        ('canned sardines', 'grow'),
        ('corned beef', 'grow'),
        ('cheese', 'grow'),
        ('mung beans', 'grow'),

        # glow
        ('ampalaya', 'glow'),
        ('bell pepper', 'glow'),
        ('cabbage', 'glow'),
        ('carrot', 'glow'),
        ('carrots', 'glow'),
        ('cauliflower', 'glow'),
        ('eggplant', 'glow'),
        ('green onions', 'glow'),
        ('kangkong', 'glow'),
        ('okra', 'glow'),
        ('chili leaves', 'glow'),
        ('green papaya', 'glow'),
        ('onion', 'glow'),
        ('bean sprouts', 'glow'),
        ('green peas', 'glow'),
        ('green beans', 'glow'),

        # other (condiments, spices, fats, liquids that would
        # double-count or don't fit any Pinggang Pinoy group)
        ('garlic', 'other'),
        ('ginger', 'other'),
        ('bay leaves', 'other'),
        ('black peppercorns', 'other'),
        ('bagoong', 'other'),
        ('fish sauce', 'other'),
        ('curry powder', 'other'),
        ('cornstarch', 'other'),
        ('brown sugar', 'other'),
        ('cooking oil', 'other'),
        ('calamansi juice', 'other'),
        ('coconut milk', 'other'),
        ('chicken broth', 'other'),
        ('liver spread', 'other'),
        ('green chili', 'other'),
    ]

    ingredient_food_groups = sa.table(
        'ingredient_food_groups',
        sa.column('id', sa.UUID()),
        sa.column('ingredient_name', sa.String()),
        sa.column('food_group', sa.String()),
    )

    import uuid
    op.bulk_insert(
        ingredient_food_groups,
        [
            {
                'id': uuid.uuid4(),
                'ingredient_name': name,
                'food_group': group,
            }
            for name, group in seed_rows
        ],
    )


def downgrade() -> None:
    op.drop_index(
        op.f('ix_ingredient_food_groups_ingredient_name'),
        table_name='ingredient_food_groups',
    )
    op.drop_table('ingredient_food_groups')