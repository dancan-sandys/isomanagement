"""merge heads before audits kpi fields

Revision ID: d0f1e2a3b4c5
Revises: 70b989015f6a, 81a2b3c4d5e6
Create Date: 2025-08-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0f1e2a3b4c5'
down_revision: Union[str, Sequence[str], None] = ('70b989015f6a', '81a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Merge-only revision; no schema changes
    pass


def downgrade() -> None:
    # Merge-only revision; no schema changes
    pass


