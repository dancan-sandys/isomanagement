"""merge heads before KPI backfill

Revision ID: 0d44dfbaf319
Revises: 30cf25339a72, e1f2a3b4c5d6
Create Date: 2025-08-15 17:51:00.397155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d44dfbaf319'
down_revision: Union[str, Sequence[str], None] = ('30cf25339a72', 'e1f2a3b4c5d6', '82b3c4d5e6f7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
