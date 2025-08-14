"""merge heads for engineering demo

Revision ID: 30cf25339a72
Revises: 6f0c3e2a, 70b989015f6a
Create Date: 2025-08-14 10:31:24.075623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30cf25339a72'
down_revision: Union[str, Sequence[str], None] = ('6f0c3e2a', '70b989015f6a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
