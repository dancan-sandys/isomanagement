"""enhance management reviews for ISO compliance

Revision ID: enhance_mgmt_reviews_iso
Revises: c9d0e1f2a3b4
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'enhance_mgmt_reviews_iso'
down_revision = 'c9d0e1f2a3b4'
branch_labels = None
depends_on = None


def upgrade():
    # Create new enums
    managementreviewtype_enum = sa.Enum('scheduled', 'ad_hoc', 'emergency', name='managementreviewtype')
    reviewinputtype_enum = sa.Enum(
        'audit_results', 'nc_capa_status', 'supplier_performance', 'kpi_metrics',
        'customer_feedback', 'risk_assessment', 'haccp_performance', 'prp_performance',
        'resource_adequacy', 'external_issues', 'internal_issues', 'previous_actions',
        name='reviewinputtype'
    )
    reviewoutputtype_enum = sa.Enum(
        'improvement_action', 'resource_allocation', 'policy_change', 'objective_update',
        'system_change', 'training_requirement', 'risk_treatment', name='reviewoutputtype'
    )
    actionpriority_enum = sa.Enum('low', 'medium', 'high', 'critical', name='actionpriority')
    actionstatus_enum = sa.Enum('assigned', 'in_progress', 'completed', 'overdue', 'cancelled', name='actionstatus')

    # Enhance management_reviews table
    with op.batch_alter_table('management_reviews') as batch_op:
        # Add new columns for ISO compliance
        batch_op.add_column(sa.Column('review_type', managementreviewtype_enum, nullable=False, server_default='scheduled'))
        batch_op.add_column(sa.Column('review_scope', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('chairperson_id', sa.Integer(), nullable=True))
        
        # ISO-required review elements
        batch_op.add_column(sa.Column('food_safety_policy_reviewed', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('food_safety_objectives_reviewed', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('fsms_changes_required', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('resource_adequacy_assessment', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('improvement_opportunities', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('previous_actions_status', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('external_issues', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('internal_issues', sa.Text(), nullable=True))
        
        # Performance data summaries
        batch_op.add_column(sa.Column('customer_feedback_summary', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('supplier_performance_summary', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('audit_results_summary', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('nc_capa_summary', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('kpi_performance_summary', sa.Text(), nullable=True))
        
        # Review documentation
        batch_op.add_column(sa.Column('minutes', sa.Text(), nullable=True))
        
        # Review effectiveness
        batch_op.add_column(sa.Column('review_effectiveness_score', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('effectiveness_justification', sa.Text(), nullable=True))
        
        # Status and scheduling
        batch_op.add_column(sa.Column('review_frequency', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
        
        # Modify existing columns to JSON for structured data
        batch_op.alter_column('attendees', type_=sa.JSON(), nullable=True)
        batch_op.alter_column('inputs', type_=sa.JSON(), nullable=True)
        batch_op.alter_column('outputs', type_=sa.JSON(), nullable=True)
        
        # Add foreign key constraints
        batch_op.create_foreign_key('fk_mgmt_review_chairperson', 'users', ['chairperson_id'], ['id'])

    # Enhance review_actions table
    with op.batch_alter_table('review_actions') as batch_op:
        # Enhanced fields for better tracking
        batch_op.add_column(sa.Column('action_type', reviewoutputtype_enum, nullable=True))
        batch_op.add_column(sa.Column('priority', actionpriority_enum, nullable=False, server_default='medium'))
        batch_op.add_column(sa.Column('status', actionstatus_enum, nullable=False, server_default='assigned'))
        
        # Progress tracking
        batch_op.add_column(sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('progress_notes', sa.Text(), nullable=True))
        
        # Completion tracking
        batch_op.add_column(sa.Column('completed_by', sa.Integer(), nullable=True))
        
        # Verification
        batch_op.add_column(sa.Column('verification_required', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'))
        batch_op.add_column(sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('verified_by', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('verification_notes', sa.Text(), nullable=True))
        
        # Resource requirements
        batch_op.add_column(sa.Column('estimated_effort_hours', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('actual_effort_hours', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('resource_requirements', sa.Text(), nullable=True))
        
        # Audit trail
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
        
        # Add foreign key constraints
        batch_op.create_foreign_key('fk_review_action_completed_by', 'users', ['completed_by'], ['id'])
        batch_op.create_foreign_key('fk_review_action_verified_by', 'users', ['verified_by'], ['id'])

    # Create management_review_inputs table
    op.create_table('management_review_inputs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('review_id', sa.Integer(), sa.ForeignKey('management_reviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('input_type', reviewinputtype_enum, nullable=False),
        sa.Column('input_source', sa.String(100), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('input_summary', sa.Text(), nullable=True),
        sa.Column('collection_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responsible_person_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        
        # Data quality indicators
        sa.Column('data_completeness_score', sa.Float(), nullable=True),
        sa.Column('data_accuracy_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        
        # Audit trail
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Create management_review_outputs table
    op.create_table('management_review_outputs',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('review_id', sa.Integer(), sa.ForeignKey('management_reviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('output_type', reviewoutputtype_enum, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Assignment and tracking
        sa.Column('assigned_to', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('target_completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('priority', actionpriority_enum, nullable=False, server_default='medium'),
        sa.Column('status', actionstatus_enum, nullable=False, server_default='assigned'),
        
        # Implementation details
        sa.Column('implementation_plan', sa.Text(), nullable=True),
        sa.Column('resource_requirements', sa.Text(), nullable=True),
        sa.Column('success_criteria', sa.Text(), nullable=True),
        
        # Progress tracking
        sa.Column('progress_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('progress_updates', sa.JSON(), nullable=True),
        
        # Completion and verification
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completion_evidence', sa.Text(), nullable=True),
        
        sa.Column('verification_required', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        
        # Impact assessment
        sa.Column('expected_impact', sa.Text(), nullable=True),
        sa.Column('actual_impact', sa.Text(), nullable=True),
        sa.Column('impact_measurement_date', sa.DateTime(timezone=True), nullable=True),
        
        # Audit trail
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Create management_review_templates table
    op.create_table('management_review_templates',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Template structure
        sa.Column('agenda_template', sa.JSON(), nullable=True),
        sa.Column('input_checklist', sa.JSON(), nullable=True),
        sa.Column('output_categories', sa.JSON(), nullable=True),
        
        # Configuration
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('review_frequency', sa.String(50), nullable=True),
        
        # Template metadata
        sa.Column('applicable_departments', sa.JSON(), nullable=True),
        sa.Column('compliance_standards', sa.JSON(), nullable=True),
        
        # Audit trail
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Create management_review_kpis table
    op.create_table('management_review_kpis',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('review_id', sa.Integer(), sa.ForeignKey('management_reviews.id'), nullable=True),
        
        # KPI details
        sa.Column('kpi_name', sa.String(200), nullable=False),
        sa.Column('kpi_description', sa.Text(), nullable=True),
        sa.Column('kpi_category', sa.String(100), nullable=True),
        
        # Measurement
        sa.Column('target_value', sa.Float(), nullable=True),
        sa.Column('actual_value', sa.Float(), nullable=True),
        sa.Column('unit_of_measure', sa.String(50), nullable=True),
        sa.Column('measurement_date', sa.DateTime(timezone=True), nullable=True),
        
        # Performance assessment
        sa.Column('performance_status', sa.String(50), nullable=True),
        sa.Column('variance_percentage', sa.Float(), nullable=True),
        sa.Column('improvement_trend', sa.String(50), nullable=True),
        
        # Audit trail
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # Create indexes for performance
    op.create_index('idx_mgmt_review_inputs_review_id', 'management_review_inputs', ['review_id'])
    op.create_index('idx_mgmt_review_inputs_type', 'management_review_inputs', ['input_type'])
    op.create_index('idx_mgmt_review_outputs_review_id', 'management_review_outputs', ['review_id'])
    op.create_index('idx_mgmt_review_outputs_type', 'management_review_outputs', ['output_type'])
    op.create_index('idx_mgmt_review_outputs_status', 'management_review_outputs', ['status'])
    op.create_index('idx_mgmt_review_kpis_review_id', 'management_review_kpis', ['review_id'])
    op.create_index('idx_review_actions_status', 'review_actions', ['status'])
    op.create_index('idx_review_actions_priority', 'review_actions', ['priority'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_review_actions_priority', 'review_actions')
    op.drop_index('idx_review_actions_status', 'review_actions')
    op.drop_index('idx_mgmt_review_kpis_review_id', 'management_review_kpis')
    op.drop_index('idx_mgmt_review_outputs_status', 'management_review_outputs')
    op.drop_index('idx_mgmt_review_outputs_type', 'management_review_outputs')
    op.drop_index('idx_mgmt_review_outputs_review_id', 'management_review_outputs')
    op.drop_index('idx_mgmt_review_inputs_type', 'management_review_inputs')
    op.drop_index('idx_mgmt_review_inputs_review_id', 'management_review_inputs')

    # Drop new tables
    op.drop_table('management_review_kpis')
    op.drop_table('management_review_templates')
    op.drop_table('management_review_outputs')
    op.drop_table('management_review_inputs')

    # Revert review_actions table changes
    with op.batch_alter_table('review_actions') as batch_op:
        batch_op.drop_constraint('fk_review_action_verified_by', type_='foreignkey')
        batch_op.drop_constraint('fk_review_action_completed_by', type_='foreignkey')
        
        batch_op.drop_column('updated_at')
        batch_op.drop_column('resource_requirements')
        batch_op.drop_column('actual_effort_hours')
        batch_op.drop_column('estimated_effort_hours')
        batch_op.drop_column('verification_notes')
        batch_op.drop_column('verified_by')
        batch_op.drop_column('verified_at')
        batch_op.drop_column('verified')
        batch_op.drop_column('verification_required')
        batch_op.drop_column('completed_by')
        batch_op.drop_column('progress_notes')
        batch_op.drop_column('progress_percentage')
        batch_op.drop_column('status')
        batch_op.drop_column('priority')
        batch_op.drop_column('action_type')

    # Revert management_reviews table changes
    with op.batch_alter_table('management_reviews') as batch_op:
        batch_op.drop_constraint('fk_mgmt_review_chairperson', type_='foreignkey')
        
        # Revert column types
        batch_op.alter_column('outputs', type_=sa.Text(), nullable=True)
        batch_op.alter_column('inputs', type_=sa.Text(), nullable=True)
        batch_op.alter_column('attendees', type_=sa.Text(), nullable=True)
        
        # Drop new columns
        batch_op.drop_column('completed_at')
        batch_op.drop_column('review_frequency')
        batch_op.drop_column('effectiveness_justification')
        batch_op.drop_column('review_effectiveness_score')
        batch_op.drop_column('minutes')
        batch_op.drop_column('kpi_performance_summary')
        batch_op.drop_column('nc_capa_summary')
        batch_op.drop_column('audit_results_summary')
        batch_op.drop_column('supplier_performance_summary')
        batch_op.drop_column('customer_feedback_summary')
        batch_op.drop_column('internal_issues')
        batch_op.drop_column('external_issues')
        batch_op.drop_column('previous_actions_status')
        batch_op.drop_column('improvement_opportunities')
        batch_op.drop_column('resource_adequacy_assessment')
        batch_op.drop_column('fsms_changes_required')
        batch_op.drop_column('food_safety_objectives_reviewed')
        batch_op.drop_column('food_safety_policy_reviewed')
        batch_op.drop_column('chairperson_id')
        batch_op.drop_column('review_scope')
        batch_op.drop_column('review_type')

    # Drop enums
    actionstatus_enum = sa.Enum(name='actionstatus')
    actionpriority_enum = sa.Enum(name='actionpriority')
    reviewoutputtype_enum = sa.Enum(name='reviewoutputtype')
    reviewinputtype_enum = sa.Enum(name='reviewinputtype')
    managementreviewtype_enum = sa.Enum(name='managementreviewtype')
    
    actionstatus_enum.drop(op.get_bind())
    actionpriority_enum.drop(op.get_bind())
    reviewoutputtype_enum.drop(op.get_bind())
    reviewinputtype_enum.drop(op.get_bind())
    managementreviewtype_enum.drop(op.get_bind())