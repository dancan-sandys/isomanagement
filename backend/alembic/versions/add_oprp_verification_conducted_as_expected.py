"""add conducted_as_expected to oprp_verification_logs

Revision ID: add_oprp_conducted
Revises: add_oprp_verification_batch_id
Create Date: 2025-03-07

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_oprp_conducted'
down_revision = 'add_oprp_verification_batch_id'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = [c['name'] for c in inspector.get_columns('oprp_verification_logs')]
    if 'conducted_as_expected' in cols:
        return
    with op.batch_alter_table('oprp_verification_logs') as batch_op:
        batch_op.add_column(sa.Column('conducted_as_expected', sa.Boolean(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('oprp_verification_logs') as batch_op:
        batch_op.drop_column('conducted_as_expected')
