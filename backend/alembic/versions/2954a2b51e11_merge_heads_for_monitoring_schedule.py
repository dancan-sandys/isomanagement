"""merge_heads_for_monitoring_schedule

Revision ID: 2954a2b51e11
Revises: 002, 1026245fd185, 3b0c4eaf1e05
Create Date: 2025-08-16 20:40:18.698841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2954a2b51e11'
down_revision: Union[str, Sequence[str], None] = ('002', '1026245fd185', '3b0c4eaf1e05')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
