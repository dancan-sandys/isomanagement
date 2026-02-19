"""add_risk_assessments_table

Revision ID: f9d9ada90919
Revises: 8944e65c5356
Create Date: 2025-08-16 15:13:45.567217

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9d9ada90919'
down_revision: Union[str, Sequence[str], None] = '8944e65c5356'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create risk_assessments table
    op.create_table('risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('non_conformance_id', sa.Integer(), nullable=False),
        sa.Column('food_safety_impact', sa.String(20), nullable=False),
        sa.Column('regulatory_impact', sa.String(20), nullable=False),
        sa.Column('customer_impact', sa.String(20), nullable=False),
        sa.Column('business_impact', sa.String(20), nullable=False),
        sa.Column('overall_risk_score', sa.Float(), nullable=False),
        sa.Column('risk_matrix_position', sa.String(10), nullable=False),
        sa.Column('requires_escalation', sa.Boolean(), default=False),
        sa.Column('escalation_level', sa.String(20)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['non_conformance_id'], ['non_conformances.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )
    
    # Add database indexes for performance
    op.create_index('ix_risk_assessments_non_conformance_id', 'risk_assessments', ['non_conformance_id'])
    op.create_index('ix_risk_assessments_created_by', 'risk_assessments', ['created_by'])
    op.create_index('ix_risk_assessments_overall_risk_score', 'risk_assessments', ['overall_risk_score'])
    op.create_index('ix_risk_assessments_requires_escalation', 'risk_assessments', ['requires_escalation'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_risk_assessments_requires_escalation', 'risk_assessments')
    op.drop_index('ix_risk_assessments_overall_risk_score', 'risk_assessments')
    op.drop_index('ix_risk_assessments_created_by', 'risk_assessments')
    op.drop_index('ix_risk_assessments_non_conformance_id', 'risk_assessments')
    
    # Drop table
    op.drop_table('risk_assessments')
