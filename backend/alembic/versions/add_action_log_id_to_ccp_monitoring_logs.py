"""add action_log_id to ccp_monitoring_logs

Revision ID: add_action_log_id_to_ccp_monitoring_logs
Revises: 20250117_enhanced_allergen_control
Create Date: 2025-01-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'add_action_log_id_to_ccp_monitoring_logs'
down_revision = '20250117_enhanced_allergen_control'
branch_labels = None
depends_on = None


def upgrade():
    """Add action_log_id column to ccp_monitoring_logs table"""
    # Get inspector to check current table structure
    inspector = inspect(op.get_bind())
    
    # Check if ccp_monitoring_logs table exists
    if 'ccp_monitoring_logs' not in inspector.get_table_names():
        print("ccp_monitoring_logs table does not exist, skipping migration")
        return
    
    # Check if action_log_id column already exists
    columns = [c['name'] for c in inspector.get_columns('ccp_monitoring_logs')]
    if 'action_log_id' in columns:
        print("action_log_id column already exists in ccp_monitoring_logs table")
        return
    
    # Add the column using batch mode for SQLite
    with op.batch_alter_table('ccp_monitoring_logs') as batch_op:
        batch_op.add_column(sa.Column('action_log_id', sa.Integer(), nullable=True))
        
        # Add index for better performance
        batch_op.create_index('ix_ccp_monitoring_logs_action_log_id', ['action_log_id'])
        
        # Add foreign key constraint if action_logs table exists
        if 'action_logs' in inspector.get_table_names():
            batch_op.create_foreign_key(
                'fk_ccp_monitoring_logs_action_log_id_action_logs',
                'action_logs', ['action_log_id'], ['id']
            )


def downgrade():
    """Remove action_log_id column from ccp_monitoring_logs table"""
    # Get inspector to check current table structure
    inspector = inspect(op.get_bind())
    
    # Check if ccp_monitoring_logs table exists
    if 'ccp_monitoring_logs' not in inspector.get_table_names():
        print("ccp_monitoring_logs table does not exist, skipping downgrade")
        return
    
    # Check if action_log_id column exists
    columns = [c['name'] for c in inspector.get_columns('ccp_monitoring_logs')]
    if 'action_log_id' not in columns:
        print("action_log_id column does not exist in ccp_monitoring_logs table")
        return
    
    # Remove the column using batch mode for SQLite
    with op.batch_alter_table('ccp_monitoring_logs') as batch_op:
        # Drop foreign key constraint if it exists
        batch_op.drop_constraint('fk_ccp_monitoring_logs_action_log_id_action_logs', type_='foreignkey')
        
        # Drop index
        batch_op.drop_index('ix_ccp_monitoring_logs_action_log_id')
        
        # Drop column
        batch_op.drop_column('action_log_id')
