"""add check constraints on meals.difficulty and profiles.sex

Revision ID: i7d8e9f0a1b2
Revises: h6c7d8e9f0a1
Create Date: 2026-09-22
"""
from typing import Sequence, Union

from alembic import op

revision: str = "i7d8e9f0a1b2"
down_revision: Union[str, None] = "h6c7d8e9f0a1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "chk_meals_difficulty",
        "meals",
        "difficulty IN ('easy', 'medium', 'hard')",
    )
    op.create_check_constraint(
        "chk_profiles_sex",
        "profiles",
        "sex IN ('Male', 'Female', 'Prefer not to say')",
    )


def downgrade() -> None:
    op.drop_constraint("chk_profiles_sex", "profiles", type_="check")
    op.drop_constraint("chk_meals_difficulty", "meals", type_="check")