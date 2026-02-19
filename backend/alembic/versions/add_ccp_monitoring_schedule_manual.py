"""add ccp monitoring schedule table

Revision ID: add_ccp_monitoring_schedule_manual
Revises: 2954a2b51e11
Create Date: 2025-08-16 20:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'add_ccp_monitoring_schedule_manual'
down_revision = '2954a2b51e11'
branch_labels = None
depends_on = None


def upgrade():
    # Create ccp_monitoring_schedules table
    op.create_table('ccp_monitoring_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ccp_id', sa.Integer(), nullable=False),
        sa.Column('schedule_type', sa.String(length=20), nullable=True),  # SQLite doesn't support ENUM
        sa.Column('interval_minutes', sa.Integer(), nullable=True),
        sa.Column('cron_expression', sa.String(length=100), nullable=True),
        sa.Column('tolerance_window_minutes', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_scheduled_time', sa.DateTime(), nullable=True),
        sa.Column('next_due_time', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ccp_id'], ['ccps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ccp_monitoring_schedules_id'), 'ccp_monitoring_schedules', ['id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_ccp_monitoring_schedules_id'), table_name='ccp_monitoring_schedules')
    op.drop_table('ccp_monitoring_schedules')
