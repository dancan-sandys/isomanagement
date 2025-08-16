"""add_hazard_reviews_table

Revision ID: 82099dc18e69
Revises: f3283d1748f7
Create Date: 2025-08-16 08:45:12.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '82099dc18e69'
down_revision: Union[str, Sequence[str], None] = 'f3283d1748f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create hazard_reviews table
    op.create_table('hazard_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hazard_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('review_status', sa.String(length=20), nullable=False),
        sa.Column('review_comments', sa.Text(), nullable=True),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hazard_identification_adequate', sa.Boolean(), nullable=False),
        sa.Column('risk_assessment_appropriate', sa.Boolean(), nullable=False),
        sa.Column('control_measures_suitable', sa.Boolean(), nullable=False),
        sa.Column('ccp_determination_correct', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hazard_reviews_id'), 'hazard_reviews', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_hazard_reviews_id'), table_name='hazard_reviews')
    op.drop_table('hazard_reviews')
