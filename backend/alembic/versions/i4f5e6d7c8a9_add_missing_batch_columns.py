"""Add missing GS1 columns and indexes to batches table

Revision ID: i4f5e6d7c8a9
Revises: 81da6fc134d5
Create Date: 2025-01-27 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'i4f5e6d7c8a9'
down_revision: Union[str, Sequence[str], None] = '81da6fc134d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add GS1-compliant identification fields to batches table
    op.add_column('batches', sa.Column('gtin', sa.String(14), nullable=True))
    op.add_column('batches', sa.Column('sscc', sa.String(18), nullable=True))
    op.add_column('batches', sa.Column('hierarchical_lot_number', sa.String(50), nullable=True))
    
    # Add enhanced traceability fields to batches table
    op.add_column('batches', sa.Column('supplier_information', sa.JSON(), nullable=True))
    op.add_column('batches', sa.Column('customer_information', sa.JSON(), nullable=True))
    op.add_column('batches', sa.Column('distribution_location', sa.String(100), nullable=True))
    
    # Create indexes for performance optimization
    op.create_index('ix_batches_gtin', 'batches', ['gtin'])
    op.create_index('ix_batches_sscc', 'batches', ['sscc'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_batches_sscc', 'batches')
    op.drop_index('ix_batches_gtin', 'batches')
    
    # Drop columns from batches table
    op.drop_column('batches', 'distribution_location')
    op.drop_column('batches', 'customer_information')
    op.drop_column('batches', 'supplier_information')
    op.drop_column('batches', 'hierarchical_lot_number')
    op.drop_column('batches', 'sscc')
    op.drop_column('batches', 'gtin')
