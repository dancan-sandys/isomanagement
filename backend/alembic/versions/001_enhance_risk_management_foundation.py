"""Enhance Risk Management Foundation

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create risk_management_framework table
    op.create_table('risk_management_framework',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_statement', sa.Text(), nullable=False),
        sa.Column('risk_appetite_statement', sa.Text(), nullable=False),
        sa.Column('risk_tolerance_levels', sa.JSON(), nullable=False),
        sa.Column('risk_criteria', sa.JSON(), nullable=False),
        sa.Column('risk_assessment_methodology', sa.Text(), nullable=False),
        sa.Column('risk_treatment_strategies', sa.JSON(), nullable=False),
        sa.Column('monitoring_review_frequency', sa.Text(), nullable=False),
        sa.Column('communication_plan', sa.Text(), nullable=False),
        sa.Column('review_cycle', sa.String(length=50), nullable=False),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_context table
    op.create_table('risk_context',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organizational_context', sa.Text(), nullable=False),
        sa.Column('external_context', sa.Text(), nullable=False),
        sa.Column('internal_context', sa.Text(), nullable=False),
        sa.Column('risk_management_context', sa.Text(), nullable=False),
        sa.Column('stakeholder_analysis', sa.JSON(), nullable=False),
        sa.Column('risk_criteria', sa.JSON(), nullable=False),
        sa.Column('review_frequency', sa.String(length=50), nullable=False),
        sa.Column('last_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Add new columns to risk_register table
    op.add_column('risk_register', sa.Column('risk_context_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_criteria_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_method', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessor_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_reviewed', sa.Boolean(), default=False))
    op.add_column('risk_register', sa.Column('risk_assessment_reviewer_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_assessment_review_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_strategy', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_plan', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_cost', sa.Float(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_benefit', sa.Float(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_timeline', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_approved', sa.Boolean(), default=False))
    op.add_column('risk_register', sa.Column('risk_treatment_approver_id', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_treatment_approval_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('residual_risk_score', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('residual_risk_level', sa.String(length=50), nullable=True))
    op.add_column('risk_register', sa.Column('residual_risk_acceptable', sa.Boolean(), nullable=True))
    op.add_column('risk_register', sa.Column('residual_risk_justification', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('monitoring_frequency', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('next_monitoring_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('monitoring_method', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('monitoring_responsible', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('review_frequency', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('review_responsible', sa.Integer(), nullable=True))
    op.add_column('risk_register', sa.Column('last_review_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('risk_register', sa.Column('review_outcome', sa.Text(), nullable=True))

    # Add foreign key constraints
    op.create_foreign_key('fk_risk_register_context', 'risk_register', 'risk_context', ['risk_context_id'], ['id'])
    op.create_foreign_key('fk_risk_register_assessor', 'risk_register', 'users', ['risk_assessor_id'], ['id'])
    op.create_foreign_key('fk_risk_register_reviewer', 'risk_register', 'users', ['risk_assessment_reviewer_id'], ['id'])
    op.create_foreign_key('fk_risk_register_approver', 'risk_register', 'users', ['risk_treatment_approver_id'], ['id'])
    op.create_foreign_key('fk_risk_register_monitoring', 'risk_register', 'users', ['monitoring_responsible'], ['id'])
    op.create_foreign_key('fk_risk_register_review_resp', 'risk_register', 'users', ['review_responsible'], ['id'])

    # Create fsms_risk_integration table
    op.create_table('fsms_risk_integration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('risk_register_item_id', sa.Integer(), nullable=False),
        sa.Column('fsms_element', sa.String(length=100), nullable=False),
        sa.Column('fsms_element_id', sa.Integer(), nullable=True),
        sa.Column('impact_on_fsms', sa.Text(), nullable=False),
        sa.Column('food_safety_objective_id', sa.Integer(), nullable=True),
        sa.Column('interested_party_impact', sa.JSON(), nullable=True),
        sa.Column('compliance_requirement', sa.Text(), nullable=True),
        sa.Column('integration_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('integrated_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['risk_register_item_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['integrated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_correlations table
    op.create_table('risk_correlations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('primary_risk_id', sa.Integer(), nullable=False),
        sa.Column('correlated_risk_id', sa.Integer(), nullable=False),
        sa.Column('correlation_type', sa.String(length=100), nullable=True),
        sa.Column('correlation_strength', sa.Integer(), nullable=True),
        sa.Column('correlation_description', sa.Text(), nullable=True),
        sa.Column('correlation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('identified_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['primary_risk_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['correlated_risk_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['identified_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_resource_allocation table
    op.create_table('risk_resource_allocation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('risk_register_item_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(length=100), nullable=True),
        sa.Column('resource_amount', sa.Float(), nullable=True),
        sa.Column('resource_unit', sa.String(length=50), nullable=True),
        sa.Column('allocation_justification', sa.Text(), nullable=True),
        sa.Column('allocation_approved', sa.Boolean(), default=False),
        sa.Column('allocation_approver_id', sa.Integer(), nullable=True),
        sa.Column('allocation_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('allocation_period', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['risk_register_item_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['allocation_approver_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_communications table
    op.create_table('risk_communications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('risk_register_item_id', sa.Integer(), nullable=False),
        sa.Column('communication_type', sa.String(length=100), nullable=True),
        sa.Column('communication_channel', sa.String(length=100), nullable=True),
        sa.Column('target_audience', sa.JSON(), nullable=True),
        sa.Column('communication_content', sa.Text(), nullable=True),
        sa.Column('communication_schedule', sa.String(length=100), nullable=True),
        sa.Column('communication_status', sa.String(length=100), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_by', sa.Integer(), nullable=True),
        sa.Column('delivery_confirmation', sa.Boolean(), default=False),
        sa.ForeignKeyConstraint(['risk_register_item_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['sent_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_kpis table
    op.create_table('risk_kpis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kpi_name', sa.String(length=200), nullable=False),
        sa.Column('kpi_description', sa.Text(), nullable=True),
        sa.Column('kpi_category', sa.String(length=100), nullable=True),
        sa.Column('kpi_formula', sa.Text(), nullable=True),
        sa.Column('kpi_target', sa.Float(), nullable=True),
        sa.Column('kpi_current_value', sa.Float(), nullable=True),
        sa.Column('kpi_unit', sa.String(length=50), nullable=True),
        sa.Column('kpi_frequency', sa.String(length=100), nullable=True),
        sa.Column('kpi_owner', sa.Integer(), nullable=True),
        sa.Column('kpi_status', sa.String(length=100), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_update', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['kpi_owner'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add new strategic categories to risk_register table
    # Note: This will be handled in the model update, not in migration


def downgrade():
    # Drop foreign key constraints
    op.drop_constraint('fk_risk_register_context', 'risk_register', type_='foreignkey')
    op.drop_constraint('fk_risk_register_assessor', 'risk_register', type_='foreignkey')
    op.drop_constraint('fk_risk_register_reviewer', 'risk_register', type_='foreignkey')
    op.drop_constraint('fk_risk_register_approver', 'risk_register', type_='foreignkey')
    op.drop_constraint('fk_risk_register_monitoring', 'risk_register', type_='foreignkey')
    op.drop_constraint('fk_risk_register_review_resp', 'risk_register', type_='foreignkey')

    # Drop new columns from risk_register table
    op.drop_column('risk_register', 'review_outcome')
    op.drop_column('risk_register', 'last_review_date')
    op.drop_column('risk_register', 'review_responsible')
    op.drop_column('risk_register', 'next_review_date')
    op.drop_column('risk_register', 'review_frequency')
    op.drop_column('risk_register', 'monitoring_responsible')
    op.drop_column('risk_register', 'monitoring_method')
    op.drop_column('risk_register', 'next_monitoring_date')
    op.drop_column('risk_register', 'monitoring_frequency')
    op.drop_column('risk_register', 'residual_risk_justification')
    op.drop_column('risk_register', 'residual_risk_acceptable')
    op.drop_column('risk_register', 'residual_risk_level')
    op.drop_column('risk_register', 'residual_risk_score')
    op.drop_column('risk_register', 'risk_treatment_approval_date')
    op.drop_column('risk_register', 'risk_treatment_approver_id')
    op.drop_column('risk_register', 'risk_treatment_approved')
    op.drop_column('risk_register', 'risk_treatment_timeline')
    op.drop_column('risk_register', 'risk_treatment_benefit')
    op.drop_column('risk_register', 'risk_treatment_cost')
    op.drop_column('risk_register', 'risk_treatment_plan')
    op.drop_column('risk_register', 'risk_treatment_strategy')
    op.drop_column('risk_register', 'risk_assessment_review_date')
    op.drop_column('risk_register', 'risk_assessment_reviewer_id')
    op.drop_column('risk_register', 'risk_assessment_reviewed')
    op.drop_column('risk_register', 'risk_assessor_id')
    op.drop_column('risk_register', 'risk_assessment_date')
    op.drop_column('risk_register', 'risk_assessment_method')
    op.drop_column('risk_register', 'risk_criteria_id')
    op.drop_column('risk_register', 'risk_context_id')

    # Drop tables
    op.drop_table('risk_kpis')
    op.drop_table('risk_communications')
    op.drop_table('risk_resource_allocation')
    op.drop_table('risk_correlations')
    op.drop_table('fsms_risk_integration')
    op.drop_table('risk_context')
    op.drop_table('risk_management_framework')
