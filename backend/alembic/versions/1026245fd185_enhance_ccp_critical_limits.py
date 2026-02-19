"""enhance_ccp_critical_limits

Revision ID: 1026245fd185
Revises: bd4abeadfe08
Create Date: 2025-08-16 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '1026245fd185'
down_revision: Union[str, Sequence[str], None] = 'bd4abeadfe08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add enhanced critical limits fields to ccps table
    with op.batch_alter_table('ccps') as batch_op:
        batch_op.add_column(sa.Column('critical_limits', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('validation_evidence', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove enhanced critical limits fields from ccps table
    with op.batch_alter_table('ccps') as batch_op:
        batch_op.drop_column('validation_evidence')
        batch_op.drop_column('critical_limits')
