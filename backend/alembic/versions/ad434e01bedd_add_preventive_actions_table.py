"""add_preventive_actions_table

Revision ID: ad434e01bedd
Revises: aa02564a297f
Create Date: 2025-08-16 15:15:05.822361

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad434e01bedd'
down_revision: Union[str, Sequence[str], None] = 'aa02564a297f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create preventive_actions table
    op.create_table('preventive_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('non_conformance_id', sa.Integer(), nullable=False),
        sa.Column('action_title', sa.String(200), nullable=False),
        sa.Column('action_description', sa.Text(), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=False),  # process_improvement, training, equipment_upgrade, procedure_update
        sa.Column('priority', sa.String(20), nullable=False),  # low, medium, high, critical
        sa.Column('assigned_to', sa.Integer(), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),  # planned, in_progress, completed, cancelled
        sa.Column('completion_date', sa.DateTime(timezone=True)),
        sa.Column('effectiveness_target', sa.Float()),  # percentage target for effectiveness
        sa.Column('effectiveness_measured', sa.Float()),  # actual effectiveness percentage
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('updated_by', sa.Integer()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['non_conformance_id'], ['non_conformances.id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    
    # Add database indexes for performance
    op.create_index('ix_preventive_actions_non_conformance_id', 'preventive_actions', ['non_conformance_id'])
    op.create_index('ix_preventive_actions_assigned_to', 'preventive_actions', ['assigned_to'])
    op.create_index('ix_preventive_actions_status', 'preventive_actions', ['status'])
    op.create_index('ix_preventive_actions_priority', 'preventive_actions', ['priority'])
    op.create_index('ix_preventive_actions_due_date', 'preventive_actions', ['due_date'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_preventive_actions_due_date', 'preventive_actions')
    op.drop_index('ix_preventive_actions_priority', 'preventive_actions')
    op.drop_index('ix_preventive_actions_status', 'preventive_actions')
    op.drop_index('ix_preventive_actions_assigned_to', 'preventive_actions')
    op.drop_index('ix_preventive_actions_non_conformance_id', 'preventive_actions')
    
    # Drop table
    op.drop_table('preventive_actions')
