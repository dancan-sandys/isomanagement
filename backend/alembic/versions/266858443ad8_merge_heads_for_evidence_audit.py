"""merge_heads_for_evidence_audit

Revision ID: 266858443ad8
Revises: 003, 2a3bd4897b81
Create Date: 2025-08-16 23:27:02.682824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '266858443ad8'
down_revision: Union[str, Sequence[str], None] = ('003', '2a3bd4897b81')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
