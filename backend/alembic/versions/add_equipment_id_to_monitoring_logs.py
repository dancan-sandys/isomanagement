"""add equipment_id to monitoring logs

Revision ID: add_equipment_id_to_monitoring_logs
Revises: add_ccp_monitoring_schedule_manual
Create Date: 2025-08-16 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_equipment_id_to_monitoring_logs'
down_revision = 'add_ccp_monitoring_schedule_manual'
branch_labels = None
depends_on = None


def upgrade():
    # Add equipment_id column to ccp_monitoring_logs table using batch mode for SQLite
    with op.batch_alter_table('ccp_monitoring_logs') as batch_op:
        batch_op.add_column(sa.Column('equipment_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_monitoring_logs_equipment', 'equipment', ['equipment_id'], ['id'])


def downgrade():
    with op.batch_alter_table('ccp_monitoring_logs') as batch_op:
        batch_op.drop_constraint('fk_monitoring_logs_equipment', type_='foreignkey')
        batch_op.drop_column('equipment_id')
