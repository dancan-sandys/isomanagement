"""merge heads for management review

Revision ID: 70b989015f6a
Revises: 6b1f4a2a1abc, c9d0e1f2a3b4
Create Date: 2025-08-12 11:28:10.629570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70b989015f6a'
down_revision: Union[str, Sequence[str], None] = ('6b1f4a2a1abc', 'c9d0e1f2a3b4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
