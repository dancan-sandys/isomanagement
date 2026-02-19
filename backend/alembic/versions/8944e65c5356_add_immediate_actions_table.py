"""add_immediate_actions_table

Revision ID: 8944e65c5356
Revises: i4f5e6d7c8a9
Create Date: 2025-08-16 15:08:37.100896

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8944e65c5356'
down_revision: Union[str, Sequence[str], None] = 'i4f5e6d7c8a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create immediate_actions table
    op.create_table('immediate_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('non_conformance_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('implemented_by', sa.Integer(), nullable=False),
        sa.Column('implemented_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('effectiveness_verified', sa.Boolean(), default=False),
        sa.Column('verification_date', sa.DateTime(timezone=True)),
        sa.Column('verification_by', sa.Integer()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['non_conformance_id'], ['non_conformances.id']),
        sa.ForeignKeyConstraint(['implemented_by'], ['users.id']),
        sa.ForeignKeyConstraint(['verification_by'], ['users.id'])
    )
    
    # Add database indexes for performance
    op.create_index('ix_immediate_actions_non_conformance_id', 'immediate_actions', ['non_conformance_id'])
    op.create_index('ix_immediate_actions_implemented_by', 'immediate_actions', ['implemented_by'])
    op.create_index('ix_immediate_actions_verification_by', 'immediate_actions', ['verification_by'])
    op.create_index('ix_immediate_actions_action_type', 'immediate_actions', ['action_type'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_immediate_actions_action_type', 'immediate_actions')
    op.drop_index('ix_immediate_actions_verification_by', 'immediate_actions')
    op.drop_index('ix_immediate_actions_implemented_by', 'immediate_actions')
    op.drop_index('ix_immediate_actions_non_conformance_id', 'immediate_actions')
    
    # Drop table
    op.drop_table('immediate_actions')
