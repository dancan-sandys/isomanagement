"""add_escalation_rules_table

Revision ID: aa02564a297f
Revises: f9d9ada90919
Create Date: 2025-08-16 15:14:30.406223

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa02564a297f'
down_revision: Union[str, Sequence[str], None] = 'f9d9ada90919'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create escalation_rules table
    op.create_table('escalation_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('rule_name', sa.String(100), nullable=False),
        sa.Column('rule_description', sa.Text()),
        sa.Column('trigger_condition', sa.String(50), nullable=False),  # risk_score, time_delay, severity_level
        sa.Column('trigger_value', sa.Float(), nullable=False),
        sa.Column('escalation_level', sa.String(20), nullable=False),  # supervisor, manager, director, executive
        sa.Column('notification_recipients', sa.Text()),  # JSON array of user IDs or email addresses
        sa.Column('escalation_timeframe', sa.Integer()),  # hours
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('updated_by', sa.Integer()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    
    # Add database indexes for performance
    op.create_index('ix_escalation_rules_trigger_condition', 'escalation_rules', ['trigger_condition'])
    op.create_index('ix_escalation_rules_escalation_level', 'escalation_rules', ['escalation_level'])
    op.create_index('ix_escalation_rules_is_active', 'escalation_rules', ['is_active'])
    op.create_index('ix_escalation_rules_created_by', 'escalation_rules', ['created_by'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_escalation_rules_created_by', 'escalation_rules')
    op.drop_index('ix_escalation_rules_is_active', 'escalation_rules')
    op.drop_index('ix_escalation_rules_escalation_level', 'escalation_rules')
    op.drop_index('ix_escalation_rules_trigger_condition', 'escalation_rules')
    
    # Drop table
    op.drop_table('escalation_rules')
