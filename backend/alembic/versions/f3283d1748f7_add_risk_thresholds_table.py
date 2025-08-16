"""add_risk_thresholds_table

Revision ID: f3283d1748f7
Revises: c12290b7f1b1
Create Date: 2025-08-16 08:26:24.768337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'f3283d1748f7'
down_revision: Union[str, Sequence[str], None] = 'c12290b7f1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create risk_thresholds table
    op.create_table('risk_thresholds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scope_type', sa.String(length=20), nullable=False),
        sa.Column('scope_id', sa.Integer(), nullable=True),
        sa.Column('low_threshold', sa.Integer(), nullable=False),
        sa.Column('medium_threshold', sa.Integer(), nullable=False),
        sa.Column('high_threshold', sa.Integer(), nullable=False),
        sa.Column('likelihood_scale', sa.Integer(), nullable=False),
        sa.Column('severity_scale', sa.Integer(), nullable=False),
        sa.Column('calculation_method', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_risk_thresholds_id'), 'risk_thresholds', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_risk_thresholds_id'), table_name='risk_thresholds')
    op.drop_table('risk_thresholds')
