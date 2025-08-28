"""add_risk_id_to_action_logs

Revision ID: ab2104282128
Revises: ad8eec8af93d
Create Date: 2025-08-27 21:55:46.191484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab2104282128'
down_revision: Union[str, Sequence[str], None] = 'ad8eec8af93d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add risk_id column to action_logs table
    op.add_column('action_logs', sa.Column('risk_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_action_logs_risk_id'), 'action_logs', ['risk_id'], unique=False)
    op.create_foreign_key(None, 'action_logs', 'risk_register', ['risk_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove risk_id column from action_logs table
    op.drop_constraint(None, 'action_logs', type_='foreignkey')
    op.drop_index(op.f('ix_action_logs_risk_id'), table_name='action_logs')
    op.drop_column('action_logs', 'risk_id')
