"""HACCP Risk Integration

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Add risk integration fields to hazards table
    op.add_column('hazards', sa.Column('risk_register_item_id', sa.Integer(), nullable=True))
    op.add_column('hazards', sa.Column('risk_assessment_method', sa.String(length=100), nullable=True))
    op.add_column('hazards', sa.Column('risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('hazards', sa.Column('risk_assessor_id', sa.Integer(), nullable=True))
    op.add_column('hazards', sa.Column('risk_treatment_plan', sa.Text(), nullable=True))
    op.add_column('hazards', sa.Column('risk_monitoring_frequency', sa.String(length=100), nullable=True))
    op.add_column('hazards', sa.Column('risk_review_frequency', sa.String(length=100), nullable=True))
    op.add_column('hazards', sa.Column('risk_control_effectiveness', sa.Integer(), nullable=True))
    op.add_column('hazards', sa.Column('risk_residual_score', sa.Integer(), nullable=True))
    op.add_column('hazards', sa.Column('risk_residual_level', sa.String(length=50), nullable=True))
    op.add_column('hazards', sa.Column('risk_acceptable', sa.Boolean(), nullable=True))
    op.add_column('hazards', sa.Column('risk_justification', sa.Text(), nullable=True))

    # Add risk integration fields to prp_programs table
    op.add_column('prp_programs', sa.Column('risk_register_item_id', sa.Integer(), nullable=True))
    op.add_column('prp_programs', sa.Column('risk_assessment_frequency', sa.String(length=100), nullable=True))
    op.add_column('prp_programs', sa.Column('risk_monitoring_plan', sa.Text(), nullable=True))
    op.add_column('prp_programs', sa.Column('risk_review_plan', sa.Text(), nullable=True))
    op.add_column('prp_programs', sa.Column('risk_improvement_plan', sa.Text(), nullable=True))
    op.add_column('prp_programs', sa.Column('risk_control_effectiveness', sa.Integer(), nullable=True))
    op.add_column('prp_programs', sa.Column('risk_residual_score', sa.Integer(), nullable=True))
    op.add_column('prp_programs', sa.Column('risk_residual_level', sa.String(length=50), nullable=True))

    # Add risk integration fields to products table
    op.add_column('products', sa.Column('risk_assessment_required', sa.Boolean(), default=True))
    op.add_column('products', sa.Column('risk_assessment_frequency', sa.String(length=100), nullable=True))
    op.add_column('products', sa.Column('risk_review_frequency', sa.String(length=100), nullable=True))
    op.add_column('products', sa.Column('last_risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('products', sa.Column('next_risk_assessment_date', sa.DateTime(timezone=True), nullable=True))

    # Add risk integration fields to process_flows table
    op.add_column('process_flows', sa.Column('risk_assessment_required', sa.Boolean(), default=True))
    op.add_column('process_flows', sa.Column('risk_assessment_frequency', sa.String(length=100), nullable=True))
    op.add_column('process_flows', sa.Column('risk_review_frequency', sa.String(length=100), nullable=True))
    op.add_column('process_flows', sa.Column('last_risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('process_flows', sa.Column('next_risk_assessment_date', sa.DateTime(timezone=True), nullable=True))

    # Add risk integration fields to ccps table
    op.add_column('ccps', sa.Column('risk_register_item_id', sa.Integer(), nullable=True))
    op.add_column('ccps', sa.Column('risk_assessment_method', sa.String(length=100), nullable=True))
    op.add_column('ccps', sa.Column('risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('ccps', sa.Column('risk_assessor_id', sa.Integer(), nullable=True))
    op.add_column('ccps', sa.Column('risk_treatment_plan', sa.Text(), nullable=True))
    op.add_column('ccps', sa.Column('risk_monitoring_frequency', sa.String(length=100), nullable=True))
    op.add_column('ccps', sa.Column('risk_review_frequency', sa.String(length=100), nullable=True))
    op.add_column('ccps', sa.Column('risk_control_effectiveness', sa.Integer(), nullable=True))
    op.add_column('ccps', sa.Column('risk_residual_score', sa.Integer(), nullable=True))
    op.add_column('ccps', sa.Column('risk_residual_level', sa.String(length=50), nullable=True))

    # Create foreign key constraints
    op.create_foreign_key('fk_hazards_risk_register', 'hazards', 'risk_register', ['risk_register_item_id'], ['id'])
    op.create_foreign_key('fk_hazards_risk_assessor', 'hazards', 'users', ['risk_assessor_id'], ['id'])
    op.create_foreign_key('fk_prp_programs_risk_register', 'prp_programs', 'risk_register', ['risk_register_item_id'], ['id'])
    op.create_foreign_key('fk_ccps_risk_register', 'ccps', 'risk_register', ['risk_register_item_id'], ['id'])
    op.create_foreign_key('fk_ccps_risk_assessor', 'ccps', 'users', ['risk_assessor_id'], ['id'])

    # Create haccp_risk_assessment table for detailed HACCP risk assessments
    op.create_table('haccp_risk_assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hazard_id', sa.Integer(), nullable=False),
        sa.Column('ccp_id', sa.Integer(), nullable=True),
        sa.Column('prp_program_id', sa.Integer(), nullable=True),
        sa.Column('assessment_type', sa.String(length=50), nullable=False),  # hazard, ccp, prp
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
        
        sa.ForeignKeyConstraint(['hazard_id'], ['hazards.id'], ),
        sa.ForeignKeyConstraint(['ccp_id'], ['ccps.id'], ),
        sa.ForeignKeyConstraint(['prp_program_id'], ['prp_programs.id'], ),
        sa.ForeignKeyConstraint(['assessor_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create haccp_risk_integration table for linking HACCP elements to risk register
    op.create_table('haccp_risk_integration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('risk_register_item_id', sa.Integer(), nullable=False),
        sa.Column('haccp_element_type', sa.String(length=50), nullable=False),  # hazard, ccp, prp, process, product
        sa.Column('haccp_element_id', sa.Integer(), nullable=False),
        sa.Column('integration_type', sa.String(length=50), nullable=False),  # direct, indirect, related
        sa.Column('integration_strength', sa.Integer(), nullable=True),  # 1-5 scale
        sa.Column('impact_description', sa.Text(), nullable=False),
        sa.Column('food_safety_impact', sa.Text(), nullable=True),
        sa.Column('compliance_impact', sa.Text(), nullable=True),
        sa.Column('operational_impact', sa.Text(), nullable=True),
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

    # Create haccp_risk_monitoring table for monitoring HACCP-related risks
    op.create_table('haccp_risk_monitoring',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('haccp_risk_assessment_id', sa.Integer(), nullable=False),
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
        
        sa.ForeignKeyConstraint(['haccp_risk_assessment_id'], ['haccp_risk_assessments.id'], ),
        sa.ForeignKeyConstraint(['monitor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create haccp_risk_reviews table for reviewing HACCP-related risks
    op.create_table('haccp_risk_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('haccp_risk_assessment_id', sa.Integer(), nullable=False),
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
        
        sa.ForeignKeyConstraint(['haccp_risk_assessment_id'], ['haccp_risk_assessments.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_hazards_risk_register', 'hazards', type_='foreignkey')
    op.drop_constraint('fk_hazards_risk_assessor', 'hazards', type_='foreignkey')
    op.drop_constraint('fk_prp_programs_risk_register', 'prp_programs', type_='foreignkey')
    op.drop_constraint('fk_ccps_risk_register', 'ccps', type_='foreignkey')
    op.drop_constraint('fk_ccps_risk_assessor', 'ccps', type_='foreignkey')

    # Drop new columns from hazards table
    op.drop_column('hazards', 'risk_justification')
    op.drop_column('hazards', 'risk_acceptable')
    op.drop_column('hazards', 'risk_residual_level')
    op.drop_column('hazards', 'risk_residual_score')
    op.drop_column('hazards', 'risk_control_effectiveness')
    op.drop_column('hazards', 'risk_review_frequency')
    op.drop_column('hazards', 'risk_monitoring_frequency')
    op.drop_column('hazards', 'risk_treatment_plan')
    op.drop_column('hazards', 'risk_assessor_id')
    op.drop_column('hazards', 'risk_assessment_date')
    op.drop_column('hazards', 'risk_assessment_method')
    op.drop_column('hazards', 'risk_register_item_id')

    # Drop new columns from prp_programs table
    op.drop_column('prp_programs', 'risk_residual_level')
    op.drop_column('prp_programs', 'risk_residual_score')
    op.drop_column('prp_programs', 'risk_control_effectiveness')
    op.drop_column('prp_programs', 'risk_improvement_plan')
    op.drop_column('prp_programs', 'risk_review_plan')
    op.drop_column('prp_programs', 'risk_monitoring_plan')
    op.drop_column('prp_programs', 'risk_assessment_frequency')
    op.drop_column('prp_programs', 'risk_register_item_id')

    # Drop new columns from products table
    op.drop_column('products', 'next_risk_assessment_date')
    op.drop_column('products', 'last_risk_assessment_date')
    op.drop_column('products', 'risk_review_frequency')
    op.drop_column('products', 'risk_assessment_frequency')
    op.drop_column('products', 'risk_assessment_required')

    # Drop new columns from process_flows table
    op.drop_column('process_flows', 'next_risk_assessment_date')
    op.drop_column('process_flows', 'last_risk_assessment_date')
    op.drop_column('process_flows', 'risk_review_frequency')
    op.drop_column('process_flows', 'risk_assessment_frequency')
    op.drop_column('process_flows', 'risk_assessment_required')

    # Drop new columns from ccps table
    op.drop_column('ccps', 'risk_residual_level')
    op.drop_column('ccps', 'risk_residual_score')
    op.drop_column('ccps', 'risk_control_effectiveness')
    op.drop_column('ccps', 'risk_review_frequency')
    op.drop_column('ccps', 'risk_monitoring_frequency')
    op.drop_column('ccps', 'risk_treatment_plan')
    op.drop_column('ccps', 'risk_assessor_id')
    op.drop_column('ccps', 'risk_assessment_date')
    op.drop_column('ccps', 'risk_assessment_method')
    op.drop_column('ccps', 'risk_register_item_id')

    # Drop tables
    op.drop_table('haccp_risk_reviews')
    op.drop_table('haccp_risk_monitoring')
    op.drop_table('haccp_risk_integration')
    op.drop_table('haccp_risk_assessments')
