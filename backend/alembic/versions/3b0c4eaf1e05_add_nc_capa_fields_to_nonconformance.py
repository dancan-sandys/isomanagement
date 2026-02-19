"""add_nc_capa_fields_to_nonconformance

Revision ID: 3b0c4eaf1e05
Revises: c4dea3fc2223
Create Date: 2025-08-16 15:20:52.129360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b0c4eaf1e05'
down_revision: Union[str, Sequence[str], None] = 'c4dea3fc2223'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new fields to non_conformances table
    op.add_column('non_conformances', sa.Column('requires_immediate_action', sa.Boolean(), nullable=True, default=False))
    op.add_column('non_conformances', sa.Column('risk_level', sa.String(20), nullable=True))
    op.add_column('non_conformances', sa.Column('escalation_status', sa.String(20), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove new fields from non_conformances table
    op.drop_column('non_conformances', 'escalation_status')
    op.drop_column('non_conformances', 'risk_level')
    op.drop_column('non_conformances', 'requires_immediate_action')
