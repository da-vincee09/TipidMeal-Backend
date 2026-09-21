"""add missing ingredient_food_groups rows

Ingredients used by the seeded meals that had no food-group
classification, found via scripts/debug_food_group_exclusions.py. Without
a row, an ingredient is silently dropped from a meal's Go/Grow/Glow
proportions.

Classification follows the same scheme as the original seed: go/grow/glow
for the Pinggang Pinoy groups, 'other' for condiments, seasonings,
liquids and sauces that don't belong to a group.

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-09-21 00:00:00.000000
"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Names are lowercase to match get_ingredient_food_group_map(), which
# lowercases and strips both sides before matching.
NEW_ROWS = [
    # go (staples: root crops, noodles)
    ('potato', 'go'),
    ('sweet potato', 'go'),
    ('rice noodles', 'go'),

    # grow (protein foods)
    ('pork belly', 'grow'),
    ('pork', 'grow'),
    ('pork liver', 'grow'),
    ('quail egg', 'grow'),
    ('shrimp', 'grow'),

    # glow (vegetables)
    ('tomato', 'glow'),
    ('radish', 'glow'),
    ('string beans', 'glow'),
    ('snow peas', 'glow'),
    ('squash', 'glow'),
    ('spinach', 'glow'),

    # other (condiments, seasonings, liquids, sauces)
    ('soy sauce', 'other'),
    ('vinegar', 'other'),
    ('water', 'other'),
    ('salt', 'other'),
    ('tomato sauce', 'other'),
    ('shrimp paste', 'other'),
    ('sinigang mix', 'other'),
]


def _table():
    return sa.table(
        'ingredient_food_groups',
        sa.column('id', sa.UUID()),
        sa.column('ingredient_name', sa.String()),
        sa.column('food_group', sa.String()),
    )


def upgrade() -> None:
    op.bulk_insert(
        _table(),
        [
            {
                'id': uuid.uuid4(),
                'ingredient_name': name,
                'food_group': group,
            }
            for name, group in NEW_ROWS
        ],
    )


def downgrade() -> None:
    table = _table()
    names = [name for name, _ in NEW_ROWS]
    op.execute(table.delete().where(table.c.ingredient_name.in_(names)))