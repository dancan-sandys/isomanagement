"""PRP & Audit Risk Integration

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Add risk integration fields to audit_programs table
    op.add_column('audit_programs', sa.Column('risk_register_item_id', sa.Integer(), nullable=True))
    op.add_column('audit_programs', sa.Column('risk_assessment_required', sa.Boolean(), default=True))
    op.add_column('audit_programs', sa.Column('risk_assessment_frequency', sa.String(length=100), nullable=True))
    op.add_column('audit_programs', sa.Column('risk_review_frequency', sa.String(length=100), nullable=True))
    op.add_column('audit_programs', sa.Column('last_risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('audit_programs', sa.Column('next_risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('audit_programs', sa.Column('risk_monitoring_plan', sa.Text(), nullable=True))
    op.add_column('audit_programs', sa.Column('risk_improvement_plan', sa.Text(), nullable=True))

    # Add risk integration fields to audits table
    op.add_column('audits', sa.Column('risk_register_item_id', sa.Integer(), nullable=True))
    op.add_column('audits', sa.Column('risk_assessment_method', sa.String(length=100), nullable=True))
    op.add_column('audits', sa.Column('risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('audits', sa.Column('risk_assessor_id', sa.Integer(), nullable=True))
    op.add_column('audits', sa.Column('risk_treatment_plan', sa.Text(), nullable=True))
    op.add_column('audits', sa.Column('risk_monitoring_frequency', sa.String(length=100), nullable=True))
    op.add_column('audits', sa.Column('risk_review_frequency', sa.String(length=100), nullable=True))
    op.add_column('audits', sa.Column('risk_control_effectiveness', sa.Integer(), nullable=True))
    op.add_column('audits', sa.Column('risk_residual_score', sa.Integer(), nullable=True))
    op.add_column('audits', sa.Column('risk_residual_level', sa.String(length=50), nullable=True))

    # Add risk integration fields to audit_findings table
    op.add_column('audit_findings', sa.Column('risk_register_item_id', sa.Integer(), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_assessment_method', sa.String(length=100), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_assessor_id', sa.Integer(), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_treatment_plan', sa.Text(), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_monitoring_frequency', sa.String(length=100), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_review_frequency', sa.String(length=100), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_control_effectiveness', sa.Integer(), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_residual_score', sa.Integer(), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_residual_level', sa.String(length=50), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_acceptable', sa.Boolean(), nullable=True))
    op.add_column('audit_findings', sa.Column('risk_justification', sa.Text(), nullable=True))

    # Create audit_risk_assessment table for detailed audit risk assessments
    op.create_table('audit_risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_id', sa.Integer(), nullable=False),
        sa.Column('audit_finding_id', sa.Integer(), nullable=True),
        sa.Column('assessment_type', sa.String(length=50), nullable=False),  # audit, finding, program
        sa.Column('assessment_method', sa.String(length=100), nullable=False),
        sa.Column('assessment_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('assessor_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_status', sa.String(length=20), default='pending'),  # pending, approved, rejected
        
        # Risk assessment details
        sa.Column('initial_risk_score', sa.Integer(), nullable=False),
        sa.Column('initial_risk_level', sa.String(length=50), nullable=False),
        sa.Column('control_effectiveness', sa.Integer(), nullable=True),  # 1-5 scale
        sa.Column('residual_risk_score', sa.Integer(), nullable=True),
        sa.Column('residual_risk_level', sa.String(length=50), nullable=True),
        sa.Column('risk_acceptable', sa.Boolean(), nullable=True),
        sa.Column('risk_justification', sa.Text(), nullable=True),
        
        # Control measures
        sa.Column('control_measures', sa.Text(), nullable=True),
        sa.Column('control_verification', sa.Text(), nullable=True),
        sa.Column('control_monitoring', sa.Text(), nullable=True),
        
        # Treatment and monitoring
        sa.Column('treatment_plan', sa.Text(), nullable=True),
        sa.Column('monitoring_frequency', sa.String(length=100), nullable=True),
        sa.Column('review_frequency', sa.String(length=100), nullable=True),
        sa.Column('next_monitoring_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], ),
        sa.ForeignKeyConstraint(['audit_finding_id'], ['audit_findings.id'], ),
        sa.ForeignKeyConstraint(['assessor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create audit_risk_integration table for linking audit elements to risk register
    op.create_table('audit_risk_integration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('risk_register_item_id', sa.Integer(), nullable=False),
        sa.Column('audit_element_type', sa.String(length=50), nullable=False),  # audit, finding, program
        sa.Column('audit_element_id', sa.Integer(), nullable=False),
        sa.Column('integration_type', sa.String(length=50), nullable=False),  # direct, indirect, related
        sa.Column('integration_strength', sa.Integer(), nullable=True),  # 1-5 scale
        sa.Column('impact_description', sa.Text(), nullable=False),
        sa.Column('compliance_impact', sa.Text(), nullable=True),
        sa.Column('operational_impact', sa.Text(), nullable=True),
        sa.Column('quality_impact', sa.Text(), nullable=True),
        sa.Column('integration_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('integrated_by', sa.Integer(), nullable=True),
        sa.Column('review_required', sa.Boolean(), default=True),
        sa.Column('review_frequency', sa.String(length=100), nullable=True),
        sa.Column('last_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['risk_register_item_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['integrated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create audit_risk_monitoring table for monitoring audit-related risks
    op.create_table('audit_risk_monitoring',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_risk_assessment_id', sa.Integer(), nullable=False),
        sa.Column('monitoring_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('monitor_id', sa.Integer(), nullable=False),
        sa.Column('monitoring_type', sa.String(length=50), nullable=False),  # routine, periodic, incident
        sa.Column('monitoring_method', sa.String(length=100), nullable=False),
        sa.Column('monitoring_result', sa.String(length=50), nullable=False),  # acceptable, unacceptable, marginal
        sa.Column('risk_score_observed', sa.Integer(), nullable=True),
        sa.Column('risk_level_observed', sa.String(length=50), nullable=True),
        sa.Column('control_effectiveness_observed', sa.Integer(), nullable=True),
        sa.Column('deviations_found', sa.Boolean(), default=False),
        sa.Column('deviation_description', sa.Text(), nullable=True),
        sa.Column('corrective_actions_required', sa.Boolean(), default=False),
        sa.Column('corrective_actions', sa.Text(), nullable=True),
        sa.Column('preventive_actions', sa.Text(), nullable=True),
        sa.Column('next_monitoring_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['audit_risk_assessment_id'], ['audit_risk_assessments.id'], ),
        sa.ForeignKeyConstraint(['monitor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create audit_risk_reviews table for reviewing audit-related risks
    op.create_table('audit_risk_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audit_risk_assessment_id', sa.Integer(), nullable=False),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('review_type', sa.String(length=50), nullable=False),  # periodic, incident, change, management
        sa.Column('review_status', sa.String(length=20), nullable=False),  # pending, approved, rejected, needs_action
        sa.Column('review_outcome', sa.String(length=50), nullable=True),  # acceptable, unacceptable, needs_improvement
        sa.Column('risk_score_reviewed', sa.Integer(), nullable=True),
        sa.Column('risk_level_reviewed', sa.String(length=50), nullable=True),
        sa.Column('control_effectiveness_reviewed', sa.Integer(), nullable=True),
        sa.Column('changes_identified', sa.Boolean(), default=False),
        sa.Column('changes_description', sa.Text(), nullable=True),
        sa.Column('actions_required', sa.Boolean(), default=False),
        sa.Column('actions_description', sa.Text(), nullable=True),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_comments', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['audit_risk_assessment_id'], ['audit_risk_assessments.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create prp_audit_integration table for linking PRP programs with audit findings
    op.create_table('prp_audit_integration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prp_program_id', sa.Integer(), nullable=False),
        sa.Column('audit_finding_id', sa.Integer(), nullable=False),
        sa.Column('integration_type', sa.String(length=50), nullable=False),  # direct, indirect, related
        sa.Column('integration_strength', sa.Integer(), nullable=True),  # 1-5 scale
        sa.Column('impact_description', sa.Text(), nullable=False),
        sa.Column('prp_impact', sa.Text(), nullable=True),
        sa.Column('audit_impact', sa.Text(), nullable=True),
        sa.Column('compliance_impact', sa.Text(), nullable=True),
        sa.Column('integration_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('integrated_by', sa.Integer(), nullable=True),
        sa.Column('review_required', sa.Boolean(), default=True),
        sa.Column('review_frequency', sa.String(length=100), nullable=True),
        sa.Column('last_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['prp_program_id'], ['prp_programs.id'], ),
        sa.ForeignKeyConstraint(['audit_finding_id'], ['audit_findings.id'], ),
        sa.ForeignKeyConstraint(['integrated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create foreign key constraints
    op.create_foreign_key('fk_audit_programs_risk_register', 'audit_programs', 'risk_register', ['risk_register_item_id'], ['id'])
    op.create_foreign_key('fk_audits_risk_register', 'audits', 'risk_register', ['risk_register_item_id'], ['id'])
    op.create_foreign_key('fk_audits_risk_assessor', 'audits', 'users', ['risk_assessor_id'], ['id'])
    op.create_foreign_key('fk_audit_findings_risk_register', 'audit_findings', 'risk_register', ['risk_register_item_id'], ['id'])
    op.create_foreign_key('fk_audit_findings_risk_assessor', 'audit_findings', 'users', ['risk_assessor_id'], ['id'])


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_audit_programs_risk_register', 'audit_programs', type_='foreignkey')
    op.drop_constraint('fk_audits_risk_register', 'audits', type_='foreignkey')
    op.drop_constraint('fk_audits_risk_assessor', 'audits', type_='foreignkey')
    op.drop_constraint('fk_audit_findings_risk_register', 'audit_findings', type_='foreignkey')
    op.drop_constraint('fk_audit_findings_risk_assessor', 'audit_findings', type_='foreignkey')

    # Drop new columns from audit_programs table
    op.drop_column('audit_programs', 'risk_improvement_plan')
    op.drop_column('audit_programs', 'risk_monitoring_plan')
    op.drop_column('audit_programs', 'next_risk_assessment_date')
    op.drop_column('audit_programs', 'last_risk_assessment_date')
    op.drop_column('audit_programs', 'risk_review_frequency')
    op.drop_column('audit_programs', 'risk_assessment_frequency')
    op.drop_column('audit_programs', 'risk_assessment_required')
    op.drop_column('audit_programs', 'risk_register_item_id')

    # Drop new columns from audits table
    op.drop_column('audits', 'risk_residual_level')
    op.drop_column('audits', 'risk_residual_score')
    op.drop_column('audits', 'risk_control_effectiveness')
    op.drop_column('audits', 'risk_review_frequency')
    op.drop_column('audits', 'risk_monitoring_frequency')
    op.drop_column('audits', 'risk_treatment_plan')
    op.drop_column('audits', 'risk_assessor_id')
    op.drop_column('audits', 'risk_assessment_date')
    op.drop_column('audits', 'risk_assessment_method')
    op.drop_column('audits', 'risk_register_item_id')

    # Drop new columns from audit_findings table
    op.drop_column('audit_findings', 'risk_justification')
    op.drop_column('audit_findings', 'risk_acceptable')
    op.drop_column('audit_findings', 'risk_residual_level')
    op.drop_column('audit_findings', 'risk_residual_score')
    op.drop_column('audit_findings', 'risk_control_effectiveness')
    op.drop_column('audit_findings', 'risk_review_frequency')
    op.drop_column('audit_findings', 'risk_monitoring_frequency')
    op.drop_column('audit_findings', 'risk_treatment_plan')
    op.drop_column('audit_findings', 'risk_assessor_id')
    op.drop_column('audit_findings', 'risk_assessment_date')
    op.drop_column('audit_findings', 'risk_assessment_method')
    op.drop_column('audit_findings', 'risk_register_item_id')

    # Drop tables
    op.drop_table('prp_audit_integration')
    op.drop_table('audit_risk_reviews')
    op.drop_table('audit_risk_monitoring')
    op.drop_table('audit_risk_integration')
    op.drop_table('audit_risk_assessments')
