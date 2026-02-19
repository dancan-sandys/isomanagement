"""Strategic Risk Management

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create risk_correlations table for identifying risk interdependencies
    op.create_table('risk_correlations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('primary_risk_id', sa.Integer(), nullable=False),
        sa.Column('correlated_risk_id', sa.Integer(), nullable=False),
        sa.Column('correlation_type', sa.String(length=50), nullable=False),  # direct, indirect, cascading, amplifying
        sa.Column('correlation_strength', sa.Integer(), nullable=False),  # 1-5 scale
        sa.Column('correlation_direction', sa.String(length=20), nullable=False),  # positive, negative, bidirectional
        sa.Column('correlation_description', sa.Text(), nullable=False),
        sa.Column('impact_analysis', sa.Text(), nullable=True),
        sa.Column('mitigation_strategy', sa.Text(), nullable=True),
        sa.Column('monitoring_required', sa.Boolean(), default=True),
        sa.Column('review_frequency', sa.String(length=100), nullable=True),
        sa.Column('last_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('identified_by', sa.Integer(), nullable=True),
        sa.Column('identified_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['primary_risk_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['correlated_risk_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['identified_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_resource_allocation table for optimizing resource allocation
    op.create_table('risk_resource_allocation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('risk_register_item_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),  # personnel, financial, equipment, time
        sa.Column('resource_name', sa.String(length=200), nullable=False),
        sa.Column('resource_description', sa.Text(), nullable=True),
        sa.Column('allocation_amount', sa.Float(), nullable=False),
        sa.Column('allocation_unit', sa.String(length=50), nullable=True),  # hours, dollars, percentage, etc.
        sa.Column('allocation_priority', sa.Integer(), nullable=False),  # 1-5 scale
        sa.Column('allocation_justification', sa.Text(), nullable=False),
        sa.Column('allocation_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('allocation_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('allocation_status', sa.String(length=20), nullable=False, default='planned'),  # planned, active, completed, cancelled
        sa.Column('actual_usage', sa.Float(), nullable=True),
        sa.Column('effectiveness_rating', sa.Integer(), nullable=True),  # 1-5 scale
        sa.Column('cost_benefit_analysis', sa.Text(), nullable=True),
        sa.Column('allocated_by', sa.Integer(), nullable=True),
        sa.Column('allocation_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['risk_register_item_id'], ['risk_register.id'], ),
        sa.ForeignKeyConstraint(['allocated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_aggregation table for aggregating related risks
    op.create_table('risk_aggregations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('aggregation_name', sa.String(length=200), nullable=False),
        sa.Column('aggregation_description', sa.Text(), nullable=True),
        sa.Column('aggregation_type', sa.String(length=50), nullable=False),  # category, process, department, project
        sa.Column('aggregation_criteria', sa.JSON(), nullable=True),  # JSON criteria for aggregation
        sa.Column('aggregated_risk_score', sa.Integer(), nullable=True),
        sa.Column('aggregated_risk_level', sa.String(length=50), nullable=True),
        sa.Column('aggregation_frequency', sa.String(length=100), nullable=True),
        sa.Column('last_aggregation_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_aggregation_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('aggregation_status', sa.String(length=20), nullable=False, default='active'),  # active, inactive, archived
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_aggregation_items table for linking risks to aggregations
    op.create_table('risk_aggregation_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('aggregation_id', sa.Integer(), nullable=False),
        sa.Column('risk_register_item_id', sa.Integer(), nullable=False),
        sa.Column('weight_factor', sa.Float(), nullable=True, default=1.0),  # Weight in aggregation calculation
        sa.Column('inclusion_reason', sa.Text(), nullable=True),
        sa.Column('added_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        
        sa.ForeignKeyConstraint(['aggregation_id'], ['risk_aggregations.id'], ),
        sa.ForeignKeyConstraint(['risk_register_item_id'], ['risk_register.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_strategic_analysis table for strategic risk analysis
    op.create_table('risk_strategic_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_name', sa.String(length=200), nullable=False),
        sa.Column('analysis_description', sa.Text(), nullable=True),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),  # scenario, sensitivity, stress_test, what_if
        sa.Column('analysis_scope', sa.JSON(), nullable=True),  # JSON scope definition
        sa.Column('analysis_parameters', sa.JSON(), nullable=True),  # JSON parameters for analysis
        sa.Column('analysis_results', sa.JSON(), nullable=True),  # JSON results
        sa.Column('key_findings', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('analysis_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('next_analysis_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('analysis_status', sa.String(length=20), nullable=False, default='completed'),  # planned, in_progress, completed, reviewed
        sa.Column('conducted_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['conducted_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_portfolio table for portfolio risk management
    op.create_table('risk_portfolios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_name', sa.String(length=200), nullable=False),
        sa.Column('portfolio_description', sa.Text(), nullable=True),
        sa.Column('portfolio_type', sa.String(length=50), nullable=False),  # business_unit, project, product, service
        sa.Column('portfolio_owner', sa.Integer(), nullable=True),
        sa.Column('portfolio_risk_appetite', sa.JSON(), nullable=True),  # JSON risk appetite definition
        sa.Column('portfolio_risk_tolerance', sa.JSON(), nullable=True),  # JSON risk tolerance levels
        sa.Column('portfolio_risk_capacity', sa.JSON(), nullable=True),  # JSON risk capacity limits
        sa.Column('portfolio_risk_score', sa.Integer(), nullable=True),
        sa.Column('portfolio_risk_level', sa.String(length=50), nullable=True),
        sa.Column('portfolio_status', sa.String(length=20), nullable=False, default='active'),  # active, inactive, archived
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(['portfolio_owner'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create risk_portfolio_items table for linking risks to portfolios
    op.create_table('risk_portfolio_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('risk_register_item_id', sa.Integer(), nullable=False),
        sa.Column('allocation_percentage', sa.Float(), nullable=True),  # Percentage allocation in portfolio
        sa.Column('contribution_to_portfolio_risk', sa.Float(), nullable=True),  # Risk contribution factor
        sa.Column('diversification_benefit', sa.Float(), nullable=True),  # Diversification benefit factor
        sa.Column('added_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        
        sa.ForeignKeyConstraint(['portfolio_id'], ['risk_portfolios.id'], ),
        sa.ForeignKeyConstraint(['risk_register_item_id'], ['risk_register.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add strategic risk fields to risk_register table
    op.add_column('risk_register', sa.Column('strategic_impact', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('business_unit', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('project_association', sa.String(length=100), nullable=True))
    op.add_column('risk_register', sa.Column('stakeholder_impact', sa.JSON(), nullable=True))
    op.add_column('risk_register', sa.Column('market_impact', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('competitive_impact', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('regulatory_impact', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('financial_impact', sa.JSON(), nullable=True))
    op.add_column('risk_register', sa.Column('operational_impact', sa.JSON(), nullable=True))
    op.add_column('risk_register', sa.Column('reputational_impact', sa.Text(), nullable=True))
    op.add_column('risk_register', sa.Column('risk_velocity', sa.String(length=50), nullable=True))  # slow, medium, fast
    op.add_column('risk_register', sa.Column('risk_persistence', sa.String(length=50), nullable=True))  # temporary, persistent, permanent
    op.add_column('risk_register', sa.Column('risk_contagion', sa.Boolean(), nullable=True))  # Can it spread to other areas
    op.add_column('risk_register', sa.Column('risk_cascade', sa.Boolean(), nullable=True))  # Can it trigger other risks
    op.add_column('risk_register', sa.Column('risk_amplification', sa.Boolean(), nullable=True))  # Can it amplify other risks


def downgrade():
    # Drop strategic risk fields from risk_register table
    op.drop_column('risk_register', 'risk_amplification')
    op.drop_column('risk_register', 'risk_cascade')
    op.drop_column('risk_register', 'risk_contagion')
    op.drop_column('risk_register', 'risk_persistence')
    op.drop_column('risk_register', 'risk_velocity')
    op.drop_column('risk_register', 'reputational_impact')
    op.drop_column('risk_register', 'operational_impact')
    op.drop_column('risk_register', 'financial_impact')
    op.drop_column('risk_register', 'regulatory_impact')
    op.drop_column('risk_register', 'competitive_impact')
    op.drop_column('risk_register', 'market_impact')
    op.drop_column('risk_register', 'stakeholder_impact')
    op.drop_column('risk_register', 'project_association')
    op.drop_column('risk_register', 'business_unit')
    op.drop_column('risk_register', 'strategic_impact')

    # Drop tables
    op.drop_table('risk_portfolio_items')
    op.drop_table('risk_portfolios')
    op.drop_table('risk_strategic_analysis')
    op.drop_table('risk_aggregation_items')
    op.drop_table('risk_aggregations')
    op.drop_table('risk_resource_allocation')
    op.drop_table('risk_correlations')

