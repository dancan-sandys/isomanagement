"""add verification and validation tables manual

Revision ID: 2a3bd4897b81
Revises: add_equipment_id_to_monitoring_logs
Create Date: 2024-12-19 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '2a3bd4897b81'
down_revision = 'add_equipment_id_to_monitoring_logs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create verification_type enum
    op.execute("CREATE TYPE verification_type AS ENUM ('record_review', 'direct_observation', 'sampling_testing', 'calibration_check')")
    
    # Create ccp_verification_programs table
    op.create_table('ccp_verification_programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ccp_id', sa.Integer(), nullable=False),
        sa.Column('verification_type', sa.Enum('record_review', 'direct_observation', 'sampling_testing', 'calibration_check', name='verification_type'), nullable=False),
        sa.Column('frequency', sa.String(length=50), nullable=False),
        sa.Column('frequency_value', sa.Integer(), nullable=True),
        sa.Column('last_verification_date', sa.DateTime(), nullable=True),
        sa.Column('next_verification_date', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('required_verifier_role', sa.String(length=50), nullable=True),
        sa.Column('verification_criteria', sa.Text(), nullable=True),
        sa.Column('sampling_plan', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ccp_id'], ['ccps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ccp_verification_programs_id'), 'ccp_verification_programs', ['id'], unique=False)
    
    # Create validation_type enum
    op.execute("CREATE TYPE validation_type AS ENUM ('process_authority_letter', 'scientific_study', 'validation_test', 'expert_opinion')")
    
    # Create validation_review_status enum
    op.execute("CREATE TYPE validation_review_status AS ENUM ('pending', 'approved', 'rejected')")
    
    # Create ccp_validations table
    op.create_table('ccp_validations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ccp_id', sa.Integer(), nullable=False),
        sa.Column('validation_type', sa.Enum('process_authority_letter', 'scientific_study', 'validation_test', 'expert_opinion', name='validation_type'), nullable=False),
        sa.Column('validation_title', sa.String(length=200), nullable=False),
        sa.Column('validation_description', sa.Text(), nullable=True),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('external_reference', sa.String(length=500), nullable=True),
        sa.Column('validation_date', sa.DateTime(), nullable=True),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('validation_result', sa.Text(), nullable=True),
        sa.Column('critical_limits_validated', sa.Text(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('review_status', sa.Enum('pending', 'approved', 'rejected', name='validation_review_status'), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ccp_id'], ['ccps.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ccp_validations_id'), 'ccp_validations', ['id'], unique=False)
    
    # Add verification_program_id to ccp_verification_logs
    with op.batch_alter_table('ccp_verification_logs') as batch_op:
        batch_op.add_column(sa.Column('verification_program_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('verifier_role', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('verification_notes', sa.Text(), nullable=True))
        batch_op.create_foreign_key('fk_verification_log_program', 'ccp_verification_programs', ['verification_program_id'], ['id'])


def downgrade() -> None:
    # Remove foreign key and columns from ccp_verification_logs
    with op.batch_alter_table('ccp_verification_logs') as batch_op:
        batch_op.drop_constraint('fk_verification_log_program', type_='foreignkey')
        batch_op.drop_column('verification_notes')
        batch_op.drop_column('verifier_role')
        batch_op.drop_column('verification_program_id')
    
    # Drop tables
    op.drop_index(op.f('ix_ccp_validations_id'), table_name='ccp_validations')
    op.drop_table('ccp_validations')
    op.drop_index(op.f('ix_ccp_verification_programs_id'), table_name='ccp_verification_programs')
    op.drop_table('ccp_verification_programs')
    
    # Drop enums
    op.execute("DROP TYPE validation_review_status")
    op.execute("DROP TYPE validation_type")
    op.execute("DROP TYPE verification_type")
