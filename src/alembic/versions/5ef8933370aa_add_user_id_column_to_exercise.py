"""add user_id column to Exercise

Revision ID: 5ef8933370aa
Revises: a700d70fbf3c
Create Date: 2026-08-04 13:53:24.345212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ef8933370aa'
down_revision: Union[str, Sequence[str], None] = 'a700d70fbf3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
