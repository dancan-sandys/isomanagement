"""equipment & maintenance expansions

Revision ID: 20250817_equipment_maintenance_expansions
Revises: add_equipment_id_to_monitoring_logs
Create Date: 2025-08-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250817_equipment_maintenance_expansions'
down_revision = 'add_equipment_id_to_monitoring_logs'
branch_labels = None
depends_on = None


def upgrade():
    # Equipment: activity flags
    with op.batch_alter_table('equipment') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column('critical_to_food_safety', sa.Boolean(), nullable=False, server_default=sa.false()))

    # Maintenance work orders: lifecycle fields
    with op.batch_alter_table('maintenance_work_orders') as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(length=20), nullable=False, server_default='PENDING'))
        batch_op.add_column(sa.Column('priority', sa.String(length=20), nullable=False, server_default='MEDIUM'))
        batch_op.add_column(sa.Column('assigned_to', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('created_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('verified_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.create_foreign_key('fk_mwo_assigned_to_user', 'users', ['assigned_to'], ['id'])
        batch_op.create_foreign_key('fk_mwo_created_by_user', 'users', ['created_by'], ['id'])
        batch_op.create_foreign_key('fk_mwo_verified_by_user', 'users', ['verified_by'], ['id'])

    # Indexes for work orders
    op.create_index('ix_mwo_due_date', 'maintenance_work_orders', ['due_date'])
    op.create_index('ix_mwo_status', 'maintenance_work_orders', ['status'])

    # Maintenance plans: PRP link
    with op.batch_alter_table('maintenance_plans') as batch_op:
        batch_op.add_column(sa.Column('prp_document_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_maintenance_plan_prp_document', 'documents', ['prp_document_id'], ['id'])

    # Calibration plans: frequency + index
    with op.batch_alter_table('calibration_plans') as batch_op:
        batch_op.add_column(sa.Column('frequency_days', sa.Integer(), nullable=False, server_default='365'))
    op.create_index('ix_calibration_plans_next_due_at', 'calibration_plans', ['next_due_at'])

    # Calibration records: ISO metadata
    with op.batch_alter_table('calibration_records') as batch_op:
        batch_op.add_column(sa.Column('certificate_number', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('calibrated_by', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('result', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('comments', sa.Text(), nullable=True))

    # Normalize maintenance_type values to lowercase to align with enum change
    op.execute("UPDATE maintenance_plans SET maintenance_type = LOWER(maintenance_type)")

    # Backfills
    # Set next_due_at for calibration plans if null
    op.execute("UPDATE calibration_plans SET next_due_at = COALESCE(next_due_at, schedule_date)")
    # Ensure work order status/priority values are set (server_default applies for new rows)
    op.execute("UPDATE maintenance_work_orders SET status = COALESCE(status, 'PENDING')")
    op.execute("UPDATE maintenance_work_orders SET priority = COALESCE(priority, 'MEDIUM')")
    # Maintenance plans next_due_at minimal backfill to current timestamp when missing
    op.execute("UPDATE maintenance_plans SET next_due_at = COALESCE(next_due_at, CURRENT_TIMESTAMP)")



def downgrade():
    # Drop indexes
    op.drop_index('ix_mwo_due_date', table_name='maintenance_work_orders')
    op.drop_index('ix_mwo_status', table_name='maintenance_work_orders')
    op.drop_index('ix_calibration_plans_next_due_at', table_name='calibration_plans')

    # Calibration records
    with op.batch_alter_table('calibration_records') as batch_op:
        batch_op.drop_column('comments')
        batch_op.drop_column('result')
        batch_op.drop_column('calibrated_by')
        batch_op.drop_column('certificate_number')

    # Calibration plans
    with op.batch_alter_table('calibration_plans') as batch_op:
        batch_op.drop_column('frequency_days')

    # Maintenance plans
    with op.batch_alter_table('maintenance_plans') as batch_op:
        batch_op.drop_constraint('fk_maintenance_plan_prp_document', type_='foreignkey')
        batch_op.drop_column('prp_document_id')

    # Maintenance work orders
    with op.batch_alter_table('maintenance_work_orders') as batch_op:
        batch_op.drop_constraint('fk_mwo_assigned_to_user', type_='foreignkey')
        batch_op.drop_constraint('fk_mwo_created_by_user', type_='foreignkey')
        batch_op.drop_constraint('fk_mwo_verified_by_user', type_='foreignkey')
        batch_op.drop_column('verified_at')
        batch_op.drop_column('verified_by')
        batch_op.drop_column('created_by')
        batch_op.drop_column('due_date')
        batch_op.drop_column('assigned_to')
        batch_op.drop_column('priority')
        batch_op.drop_column('status')

    # Equipment
    with op.batch_alter_table('equipment') as batch_op:
        batch_op.drop_column('critical_to_food_safety')
        batch_op.drop_column('is_active')