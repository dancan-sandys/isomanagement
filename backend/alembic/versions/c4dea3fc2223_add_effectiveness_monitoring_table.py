"""add_effectiveness_monitoring_table

Revision ID: c4dea3fc2223
Revises: ad434e01bedd
Create Date: 2025-08-16 15:15:52.210626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4dea3fc2223'
down_revision: Union[str, Sequence[str], None] = 'ad434e01bedd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create effectiveness_monitoring table
    op.create_table('effectiveness_monitoring',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('non_conformance_id', sa.Integer(), nullable=False),
        sa.Column('monitoring_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('monitoring_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        sa.Column('metric_description', sa.Text()),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('actual_value', sa.Float()),
        sa.Column('measurement_unit', sa.String(20)),  # percentage, count, days, etc.
        sa.Column('measurement_frequency', sa.String(20), nullable=False),  # daily, weekly, monthly, quarterly
        sa.Column('measurement_method', sa.Text()),  # how the measurement is taken
        sa.Column('status', sa.String(20), nullable=False),  # active, completed, suspended
        sa.Column('achievement_percentage', sa.Float()),  # calculated field
        sa.Column('trend_analysis', sa.Text()),  # JSON data for trend analysis
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('updated_by', sa.Integer()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['non_conformance_id'], ['non_conformances.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'])
    )
    
    # Add database indexes for performance
    op.create_index('ix_effectiveness_monitoring_non_conformance_id', 'effectiveness_monitoring', ['non_conformance_id'])
    op.create_index('ix_effectiveness_monitoring_metric_name', 'effectiveness_monitoring', ['metric_name'])
    op.create_index('ix_effectiveness_monitoring_status', 'effectiveness_monitoring', ['status'])
    op.create_index('ix_effectiveness_monitoring_measurement_frequency', 'effectiveness_monitoring', ['measurement_frequency'])
    op.create_index('ix_effectiveness_monitoring_period_start', 'effectiveness_monitoring', ['monitoring_period_start'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_effectiveness_monitoring_period_start', 'effectiveness_monitoring')
    op.drop_index('ix_effectiveness_monitoring_measurement_frequency', 'effectiveness_monitoring')
    op.drop_index('ix_effectiveness_monitoring_status', 'effectiveness_monitoring')
    op.drop_index('ix_effectiveness_monitoring_metric_name', 'effectiveness_monitoring')
    op.drop_index('ix_effectiveness_monitoring_non_conformance_id', 'effectiveness_monitoring')
    
    # Drop table
    op.drop_table('effectiveness_monitoring')
