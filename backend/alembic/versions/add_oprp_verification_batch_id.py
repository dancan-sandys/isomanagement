"""add batch_id to oprp_verification_logs

Revision ID: add_oprp_verification_batch_id
Revises: merge_haccp_verification_heads
Create Date: 2025-03-07

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_oprp_verification_batch_id'
down_revision = 'merge_haccp_verification_heads'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c['name'] for c in inspector.get_columns('oprp_verification_logs')]
    if 'batch_id' in cols:
        return
    with op.batch_alter_table('oprp_verification_logs') as batch_op:
        batch_op.add_column(sa.Column('batch_id', sa.Integer(), nullable=True))
        existing_indexes = [ix['name'] for ix in inspector.get_indexes('oprp_verification_logs')]
        if 'ix_oprp_verification_logs_oprp_batch' not in existing_indexes:
            batch_op.create_index('ix_oprp_verification_logs_oprp_batch', ['oprp_id', 'batch_id'])


def downgrade() -> None:
    with op.batch_alter_table('oprp_verification_logs') as batch_op:
        batch_op.drop_index('ix_oprp_verification_logs_oprp_batch')
        batch_op.drop_column('batch_id')
