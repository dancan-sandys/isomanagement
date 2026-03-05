"""add haccp_verification_records table

Revision ID: add_haccp_verification_records
Revises: 
Create Date: 2025-03-04

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_haccp_verification_records'
down_revision = '20250817_equipment_maintenance_expansions'  # Set to your current head if different
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'haccp_verification_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('record_type', sa.String(20), nullable=False),
        sa.Column('ccp_id', sa.Integer(), nullable=True),
        sa.Column('oprp_id', sa.Integer(), nullable=True),
        sa.Column('monitoring_log_id', sa.Integer(), nullable=True),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('verified_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['ccp_id'], ['ccps.id'], ),
        sa.ForeignKeyConstraint(['oprp_id'], ['oprps.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
    )
    op.create_index(op.f('ix_haccp_verification_records_id'), 'haccp_verification_records', ['id'], unique=False)
    op.create_index(op.f('ix_haccp_verification_records_record_type'), 'haccp_verification_records', ['record_type'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_haccp_verification_records_record_type'), table_name='haccp_verification_records')
    op.drop_index(op.f('ix_haccp_verification_records_id'), table_name='haccp_verification_records')
    op.drop_table('haccp_verification_records')
