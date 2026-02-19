"""add batch_id to ccp_monitoring_logs

Revision ID: 82b3c4d5e6f7
Revises: 81a2b3c4d5e6
Create Date: 2025-08-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '82b3c4d5e6f7'
down_revision = '81a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use batch mode for SQLite to add column and index. Guard if column already exists.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c['name'] for c in inspector.get_columns('ccp_monitoring_logs')]
    with op.batch_alter_table('ccp_monitoring_logs') as batch_op:
        if 'batch_id' not in cols:
            batch_op.add_column(sa.Column('batch_id', sa.Integer(), nullable=True))
        # Create index only if not present
        existing_indexes = [ix['name'] for ix in inspector.get_indexes('ccp_monitoring_logs')]
        if 'ix_ccp_monitoring_logs_batch' not in existing_indexes:
            batch_op.create_index('ix_ccp_monitoring_logs_batch', ['batch_id'])
    # SQLite cannot add FK constraints without table rebuild; skip FK on SQLite


def downgrade() -> None:
    with op.batch_alter_table('ccp_monitoring_logs') as batch_op:
        batch_op.drop_index('ix_ccp_monitoring_logs_batch')
        batch_op.drop_column('batch_id')


