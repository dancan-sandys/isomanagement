"""add_product_risk_config_table

Revision ID: ecfb85dde236
Revises: 82099dc18e69
Create Date: 2025-08-16 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'ecfb85dde236'
down_revision: Union[str, Sequence[str], None] = '82099dc18e69'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create product_risk_configs table
    op.create_table('product_risk_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('calculation_method', sa.String(length=20), nullable=False),
        sa.Column('likelihood_scale', sa.Integer(), nullable=False),
        sa.Column('severity_scale', sa.Integer(), nullable=False),
        sa.Column('low_threshold', sa.Integer(), nullable=False),
        sa.Column('medium_threshold', sa.Integer(), nullable=False),
        sa.Column('high_threshold', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('product_id')
    )
    op.create_index(op.f('ix_product_risk_configs_id'), 'product_risk_configs', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_product_risk_configs_id'), table_name='product_risk_configs')
    op.drop_table('product_risk_configs')
