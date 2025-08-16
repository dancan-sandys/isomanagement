"""Enhance PRP module for ISO 22002-1:2025 compliance

Revision ID: g2f3e4d5c6a7
Revises: f1e2d3c4b5a6
Create Date: 2025-01-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'g2f3e4d5c6a7'
down_revision: Union[str, Sequence[str], None] = 'f1e2d3c4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create PRP programs table if it doesn't exist
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    if 'prp_programs' not in inspector.get_table_names():
        op.create_table(
            'prp_programs',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('program_code', sa.String(50), unique=True, nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text),
            sa.Column('category', sa.String(50), nullable=False),
            sa.Column('status', sa.String(20), nullable=False, server_default='active'),
            sa.Column('objective', sa.Text, nullable=False),
            sa.Column('scope', sa.Text, nullable=False),
            sa.Column('responsible_department', sa.String(100), nullable=False),
            sa.Column('responsible_person', sa.Integer, nullable=False),
            sa.Column('risk_assessment_required', sa.Boolean, nullable=False, server_default='1'),
            sa.Column('risk_level', sa.String(20)),
            sa.Column('frequency', sa.String(20), nullable=False),
            sa.Column('frequency_details', sa.Text),
            sa.Column('next_due_date', sa.DateTime),
            sa.Column('sop_reference', sa.String(100), nullable=False),
            sa.Column('forms_required', sa.Text),
            sa.Column('records_required', sa.Text),
            sa.Column('training_requirements', sa.Text),
            sa.Column('monitoring_frequency', sa.Text),
            sa.Column('verification_frequency', sa.Text),
            sa.Column('acceptance_criteria', sa.Text),
            sa.Column('trend_analysis_required', sa.Boolean, nullable=False, server_default='0'),
            sa.Column('corrective_action_procedure', sa.Text),
            sa.Column('escalation_procedure', sa.Text),
            sa.Column('preventive_action_procedure', sa.Text),
            sa.Column('last_review_date', sa.DateTime),
            sa.Column('next_review_date', sa.DateTime),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create PRP checklists table if it doesn't exist
    if 'prp_checklists' not in inspector.get_table_names():
        op.create_table(
            'prp_checklists',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('program_id', sa.Integer, sa.ForeignKey('prp_programs.id', ondelete='CASCADE'), nullable=False),
            sa.Column('checklist_code', sa.String(50), unique=True, nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text),
            sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
            sa.Column('scheduled_date', sa.DateTime, nullable=False),
            sa.Column('due_date', sa.DateTime, nullable=False),
            sa.Column('completed_date', sa.DateTime),
            sa.Column('assigned_to', sa.Integer, nullable=False),
            sa.Column('total_items', sa.Integer, server_default='0'),
            sa.Column('passed_items', sa.Integer, server_default='0'),
            sa.Column('failed_items', sa.Integer, server_default='0'),
            sa.Column('not_applicable_items', sa.Integer, server_default='0'),
            sa.Column('compliance_percentage', sa.Float, server_default='0.0'),
            sa.Column('general_comments', sa.Text),
            sa.Column('corrective_actions_required', sa.Boolean, server_default='0'),
            sa.Column('corrective_actions', sa.Text),
            sa.Column('evidence_files', sa.Text),  # JSON string
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create PRP checklist items table if it doesn't exist
    if 'prp_checklist_items' not in inspector.get_table_names():
        op.create_table(
            'prp_checklist_items',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('checklist_id', sa.Integer, sa.ForeignKey('prp_checklists.id', ondelete='CASCADE'), nullable=False),
            sa.Column('item_number', sa.Integer, nullable=False),
            sa.Column('question', sa.Text, nullable=False),
            sa.Column('description', sa.Text),
            sa.Column('response_type', sa.String(20), nullable=False),
            sa.Column('response_options', sa.Text),
            sa.Column('expected_response', sa.String(100)),
            sa.Column('is_critical', sa.Boolean, server_default='0'),
            sa.Column('points', sa.Integer, server_default='1'),
            sa.Column('response', sa.String(100)),
            sa.Column('response_value', sa.String(100)),
            sa.Column('is_compliant', sa.Boolean),
            sa.Column('comments', sa.Text),
            sa.Column('evidence_files', sa.Text),  # JSON string
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create PRP templates table if it doesn't exist
    if 'prp_templates' not in inspector.get_table_names():
        op.create_table(
            'prp_templates',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('template_code', sa.String(50), unique=True, nullable=False),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text),
            sa.Column('category', sa.String(50), nullable=False),
            sa.Column('template_type', sa.String(50), nullable=False),
            sa.Column('template_content', sa.Text),
            sa.Column('version', sa.String(20), nullable=False, server_default='1.0'),
            sa.Column('status', sa.String(20), nullable=False, server_default='active'),
            sa.Column('frequency', sa.String(20)),
            sa.Column('estimated_duration', sa.Integer),  # minutes
            sa.Column('required_training', sa.Text),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create PRP schedules table if it doesn't exist
    if 'prp_schedules' not in inspector.get_table_names():
        op.create_table(
            'prp_schedules',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('program_id', sa.Integer, sa.ForeignKey('prp_programs.id', ondelete='CASCADE'), nullable=False),
            sa.Column('schedule_type', sa.String(50), nullable=False),
            sa.Column('frequency', sa.String(20), nullable=False),
            sa.Column('start_date', sa.DateTime, nullable=False),
            sa.Column('end_date', sa.DateTime),
            sa.Column('next_due_date', sa.DateTime, nullable=False),
            sa.Column('preferred_time_start', sa.String(10)),
            sa.Column('preferred_time_end', sa.String(10)),
            sa.Column('day_of_week', sa.Integer),
            sa.Column('day_of_month', sa.Integer),
            sa.Column('default_assignee', sa.Integer),
            sa.Column('reminder_days_before', sa.Integer, server_default='1'),
            sa.Column('escalation_days_after', sa.Integer, server_default='1'),
            sa.Column('is_active', sa.Boolean, server_default='1'),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create risk matrices table
    if 'prp_risk_matrices' not in inspector.get_table_names():
        op.create_table(
            'prp_risk_matrices',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text),
            sa.Column('likelihood_levels', sa.Text),  # JSON string
            sa.Column('severity_levels', sa.Text),    # JSON string
            sa.Column('risk_levels', sa.Text),        # JSON string
            sa.Column('is_default', sa.Boolean, server_default='0'),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create risk assessments table
    if 'prp_risk_assessments' not in inspector.get_table_names():
        op.create_table(
            'prp_risk_assessments',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('program_id', sa.Integer, sa.ForeignKey('prp_programs.id', ondelete='CASCADE'), nullable=False),
            sa.Column('assessment_code', sa.String(50), unique=True, nullable=False),
            sa.Column('hazard_identified', sa.Text, nullable=False),
            sa.Column('hazard_description', sa.Text),
            sa.Column('likelihood_level', sa.String(50), nullable=False),
            sa.Column('severity_level', sa.String(50), nullable=False),
            sa.Column('risk_level', sa.String(20)),
            sa.Column('risk_score', sa.Integer),
            sa.Column('acceptability', sa.Boolean),
            sa.Column('existing_controls', sa.Text),
            sa.Column('additional_controls_required', sa.Text),
            sa.Column('control_effectiveness', sa.Text),
            sa.Column('residual_risk_level', sa.String(20)),
            sa.Column('residual_risk_score', sa.Integer),
            sa.Column('assessment_date', sa.DateTime, nullable=False),
            sa.Column('next_review_date', sa.DateTime),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create risk controls table
    if 'prp_risk_controls' not in inspector.get_table_names():
        op.create_table(
            'prp_risk_controls',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('risk_assessment_id', sa.Integer, sa.ForeignKey('prp_risk_assessments.id', ondelete='CASCADE'), nullable=False),
            sa.Column('control_code', sa.String(50), unique=True, nullable=False),
            sa.Column('control_type', sa.String(50), nullable=False),
            sa.Column('control_description', sa.Text, nullable=False),
            sa.Column('control_procedure', sa.Text),
            sa.Column('responsible_person', sa.Integer),
            sa.Column('implementation_date', sa.DateTime),
            sa.Column('frequency', sa.String(20)),
            sa.Column('effectiveness_measure', sa.Text),
            sa.Column('effectiveness_threshold', sa.Text),
            sa.Column('effectiveness_score', sa.Integer),
            sa.Column('is_implemented', sa.Boolean, server_default='0'),
            sa.Column('implementation_status', sa.String(20), server_default='planned'),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create corrective actions table
    if 'prp_corrective_actions' not in inspector.get_table_names():
        op.create_table(
            'prp_corrective_actions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('action_code', sa.String(50), unique=True, nullable=False),
            sa.Column('source_type', sa.String(50), nullable=False),
            sa.Column('source_id', sa.Integer, nullable=False),
            sa.Column('checklist_id', sa.Integer, sa.ForeignKey('prp_checklists.id', ondelete='SET NULL')),
            sa.Column('program_id', sa.Integer, sa.ForeignKey('prp_programs.id', ondelete='CASCADE'), nullable=False),
            sa.Column('non_conformance_description', sa.Text, nullable=False),
            sa.Column('non_conformance_date', sa.DateTime, nullable=False),
            sa.Column('severity', sa.String(50), nullable=False),
            sa.Column('immediate_cause', sa.Text),
            sa.Column('root_cause_analysis', sa.Text),
            sa.Column('root_cause_category', sa.String(50)),
            sa.Column('action_description', sa.Text, nullable=False),
            sa.Column('action_type', sa.String(50), nullable=False),
            sa.Column('responsible_person', sa.Integer, nullable=False),
            sa.Column('assigned_to', sa.Integer, nullable=False),
            sa.Column('target_completion_date', sa.DateTime, nullable=False),
            sa.Column('actual_completion_date', sa.DateTime),
            sa.Column('effectiveness_criteria', sa.Text),
            sa.Column('effectiveness_verified', sa.Boolean, server_default='0'),
            sa.Column('verification_date', sa.DateTime),
            sa.Column('verified_by', sa.Integer),
            sa.Column('status', sa.String(20), nullable=False, server_default='open'),
            sa.Column('priority', sa.String(20), server_default='medium'),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Create preventive actions table
    if 'prp_preventive_actions' not in inspector.get_table_names():
        op.create_table(
            'prp_preventive_actions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('action_code', sa.String(50), unique=True, nullable=False),
            sa.Column('trigger_type', sa.String(50), nullable=False),
            sa.Column('trigger_description', sa.Text, nullable=False),
            sa.Column('program_id', sa.Integer, sa.ForeignKey('prp_programs.id', ondelete='CASCADE'), nullable=False),
            sa.Column('action_description', sa.Text, nullable=False),
            sa.Column('objective', sa.Text, nullable=False),
            sa.Column('responsible_person', sa.Integer, nullable=False),
            sa.Column('assigned_to', sa.Integer, nullable=False),
            sa.Column('implementation_plan', sa.Text),
            sa.Column('resources_required', sa.Text),
            sa.Column('budget_estimate', sa.Float),
            sa.Column('planned_start_date', sa.DateTime),
            sa.Column('planned_completion_date', sa.DateTime),
            sa.Column('actual_start_date', sa.DateTime),
            sa.Column('actual_completion_date', sa.DateTime),
            sa.Column('success_criteria', sa.Text),
            sa.Column('effectiveness_measured', sa.Boolean, server_default='0'),
            sa.Column('effectiveness_score', sa.Integer),
            sa.Column('effectiveness_date', sa.DateTime),
            sa.Column('status', sa.String(20), nullable=False, server_default='planned'),
            sa.Column('priority', sa.String(20), server_default='medium'),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, nullable=False),
            sa.Column('updated_at', sa.DateTime),
        )

    # Add indexes for better performance
    op.create_index('idx_prp_programs_category', 'prp_programs', ['category'])
    op.create_index('idx_prp_programs_status', 'prp_programs', ['status'])
    op.create_index('idx_prp_programs_frequency', 'prp_programs', ['frequency'])
    op.create_index('idx_prp_checklists_program_id', 'prp_checklists', ['program_id'])
    op.create_index('idx_prp_checklists_status', 'prp_checklists', ['status'])
    op.create_index('idx_prp_checklists_due_date', 'prp_checklists', ['due_date'])
    op.create_index('idx_prp_checklist_items_checklist_id', 'prp_checklist_items', ['checklist_id'])
    op.create_index('idx_prp_risk_assessments_program_id', 'prp_risk_assessments', ['program_id'])
    op.create_index('idx_prp_risk_assessments_risk_level', 'prp_risk_assessments', ['risk_level'])
    op.create_index('idx_prp_risk_controls_assessment_id', 'prp_risk_controls', ['risk_assessment_id'])
    op.create_index('idx_prp_corrective_actions_program_id', 'prp_corrective_actions', ['program_id'])
    op.create_index('idx_prp_corrective_actions_status', 'prp_corrective_actions', ['status'])
    op.create_index('idx_prp_preventive_actions_program_id', 'prp_preventive_actions', ['program_id'])
    op.create_index('idx_prp_preventive_actions_status', 'prp_preventive_actions', ['status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_prp_preventive_actions_status', 'prp_preventive_actions')
    op.drop_index('idx_prp_preventive_actions_program_id', 'prp_preventive_actions')
    op.drop_index('idx_prp_corrective_actions_status', 'prp_corrective_actions')
    op.drop_index('idx_prp_corrective_actions_program_id', 'prp_corrective_actions')
    op.drop_index('idx_prp_risk_controls_assessment_id', 'prp_risk_controls')
    op.drop_index('idx_prp_risk_assessments_risk_level', 'prp_risk_assessments')
    op.drop_index('idx_prp_risk_assessments_program_id', 'prp_risk_assessments')
    op.drop_index('idx_prp_checklist_items_checklist_id', 'prp_checklist_items')
    op.drop_index('idx_prp_checklists_due_date', 'prp_checklists')
    op.drop_index('idx_prp_checklists_status', 'prp_checklists')
    op.drop_index('idx_prp_checklists_program_id', 'prp_checklists')
    op.drop_index('idx_prp_programs_frequency', 'prp_programs')
    op.drop_index('idx_prp_programs_status', 'prp_programs')
    op.drop_index('idx_prp_programs_category', 'prp_programs')

    # Drop tables in reverse order
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    
    if 'prp_preventive_actions' in inspector.get_table_names():
        op.drop_table('prp_preventive_actions')
    
    if 'prp_corrective_actions' in inspector.get_table_names():
        op.drop_table('prp_corrective_actions')
    
    if 'prp_risk_controls' in inspector.get_table_names():
        op.drop_table('prp_risk_controls')
    
    if 'prp_risk_assessments' in inspector.get_table_names():
        op.drop_table('prp_risk_assessments')
    
    if 'prp_risk_matrices' in inspector.get_table_names():
        op.drop_table('prp_risk_matrices')
    
    if 'prp_schedules' in inspector.get_table_names():
        op.drop_table('prp_schedules')
    
    if 'prp_templates' in inspector.get_table_names():
        op.drop_table('prp_templates')
    
    if 'prp_checklist_items' in inspector.get_table_names():
        op.drop_table('prp_checklist_items')
    
    if 'prp_checklists' in inspector.get_table_names():
        op.drop_table('prp_checklists')
    
    if 'prp_programs' in inspector.get_table_names():
        op.drop_table('prp_programs')
