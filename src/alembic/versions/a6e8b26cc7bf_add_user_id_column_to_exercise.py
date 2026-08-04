"""Add user_id column to Exercise

Revision ID: a6e8b26cc7bf
Revises: 5ef8933370aa
Create Date: 2026-08-04 13:57:08.071337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6e8b26cc7bf'
down_revision: Union[str, Sequence[str], None] = '5ef8933370aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
