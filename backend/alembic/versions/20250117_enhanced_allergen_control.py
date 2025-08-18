"""Enhanced allergen control models

Revision ID: 20250117_enhanced_allergen_control
Revises: 6b1f4a2a1abc
Create Date: 2025-01-17 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250117_enhanced_allergen_control'
down_revision: Union[str, Sequence[str], None] = '6b1f4a2a1abc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    # Create enum types
    op.execute("CREATE TYPE allergenflagseverity AS ENUM ('low', 'medium', 'high', 'critical')")
    op.execute("CREATE TYPE allergenflagstatus AS ENUM ('active', 'resolved', 'dismissed')")
    op.execute("CREATE TYPE allergendetectionlocation AS ENUM ('ingredient', 'process', 'packaging', 'equipment', 'environment')")
    op.execute("CREATE TYPE regulatoryregion AS ENUM ('US', 'EU', 'CA', 'AU', 'UK', 'JP', 'CN')")
    op.execute("CREATE TYPE compliancevalidationstatus AS ENUM ('compliant', 'compliant_with_warnings', 'non_compliant', 'pending_review')")

    # Create allergen_flags table
    if 'allergen_flags' not in existing:
        op.create_table(
            'allergen_flags',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('assessment_id', sa.Integer, sa.ForeignKey('product_allergen_assessments.id', ondelete='CASCADE'), nullable=True, index=True),
            sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('allergen_type', sa.String(length=100), nullable=False),
            sa.Column('detected_in', sa.Enum('ingredient', 'process', 'packaging', 'equipment', 'environment', name='allergendetectionlocation'), nullable=False),
            sa.Column('severity', sa.Enum('low', 'medium', 'high', 'critical', name='allergenflagseverity'), nullable=False, server_default='medium'),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text, nullable=False),
            sa.Column('immediate_action', sa.Text, nullable=False),
            sa.Column('detected_by', sa.Integer, nullable=False),
            sa.Column('detected_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('resolved_at', sa.DateTime),
            sa.Column('resolution_notes', sa.Text),
            sa.Column('status', sa.Enum('active', 'resolved', 'dismissed', name='allergenflagstatus'), nullable=False, server_default='active'),
            sa.Column('nc_id', sa.Integer, sa.ForeignKey('nonconformances.id', ondelete='SET NULL'), nullable=True),
            sa.Column('metadata', sa.JSON),
            sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        )

    # Create allergen_control_points table
    if 'allergen_control_points' not in existing:
        op.create_table(
            'allergen_control_points',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('process_step', sa.String(length=255), nullable=False),
            sa.Column('allergen_hazard', sa.String(length=100), nullable=False),
            sa.Column('control_measure', sa.Text, nullable=False),
            sa.Column('critical_limit', sa.String(length=255)),
            sa.Column('monitoring_procedure', sa.Text),
            sa.Column('corrective_action', sa.Text),
            sa.Column('verification_procedure', sa.Text),
            sa.Column('is_ccp', sa.Boolean, server_default=sa.text('false')),
            sa.Column('risk_level', sa.Enum('low', 'medium', 'high', name='allergenrisklevel'), nullable=False, server_default='medium'),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        )

    # Create regulatory_compliance_matrix table
    if 'regulatory_compliance_matrix' not in existing:
        op.create_table(
            'regulatory_compliance_matrix',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('region', sa.Enum('US', 'EU', 'CA', 'AU', 'UK', 'JP', 'CN', name='regulatoryregion'), nullable=False, index=True),
            sa.Column('regulation_code', sa.String(length=50), nullable=False),
            sa.Column('requirement_type', sa.String(length=50), nullable=False),
            sa.Column('requirement_text', sa.Text, nullable=False),
            sa.Column('requirement_details', sa.JSON),
            sa.Column('is_mandatory', sa.Boolean, server_default=sa.text('true')),
            sa.Column('effective_date', sa.DateTime),
            sa.Column('expiry_date', sa.DateTime),
            sa.Column('created_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
        )

    # Create label_compliance_validations table
    if 'label_compliance_validations' not in existing:
        op.create_table(
            'label_compliance_validations',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('template_id', sa.Integer, sa.ForeignKey('label_templates.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('version_id', sa.Integer, sa.ForeignKey('label_template_versions.id', ondelete='CASCADE'), nullable=True, index=True),
            sa.Column('region', sa.Enum('US', 'EU', 'CA', 'AU', 'UK', 'JP', 'CN', name='regulatoryregion'), nullable=False),
            sa.Column('compliance_score', sa.Integer, nullable=False),
            sa.Column('status', sa.Enum('compliant', 'compliant_with_warnings', 'non_compliant', 'pending_review', name='compliancevalidationstatus'), nullable=False, server_default='pending_review'),
            sa.Column('validation_results', sa.JSON, nullable=False),
            sa.Column('recommendations', sa.JSON),
            sa.Column('validated_by', sa.Integer, nullable=False),
            sa.Column('validated_at', sa.DateTime, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('expires_at', sa.DateTime),
        )

    # Create indexes for performance
    op.create_index('idx_allergen_flags_product_severity', 'allergen_flags', ['product_id', 'severity'])
    op.create_index('idx_allergen_flags_status_detected', 'allergen_flags', ['status', 'detected_at'])
    op.create_index('idx_control_points_product_ccp', 'allergen_control_points', ['product_id', 'is_ccp'])
    op.create_index('idx_compliance_matrix_region_type', 'regulatory_compliance_matrix', ['region', 'requirement_type'])
    op.create_index('idx_compliance_validations_template_region', 'label_compliance_validations', ['template_id', 'region'])


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    # Drop indexes
    op.drop_index('idx_compliance_validations_template_region', table_name='label_compliance_validations')
    op.drop_index('idx_compliance_matrix_region_type', table_name='regulatory_compliance_matrix')
    op.drop_index('idx_control_points_product_ccp', table_name='allergen_control_points')
    op.drop_index('idx_allergen_flags_status_detected', table_name='allergen_flags')
    op.drop_index('idx_allergen_flags_product_severity', table_name='allergen_flags')

    # Drop tables
    if 'label_compliance_validations' in existing:
        op.drop_table('label_compliance_validations')
    if 'regulatory_compliance_matrix' in existing:
        op.drop_table('regulatory_compliance_matrix')
    if 'allergen_control_points' in existing:
        op.drop_table('allergen_control_points')
    if 'allergen_flags' in existing:
        op.drop_table('allergen_flags')

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS compliancevalidationstatus")
    op.execute("DROP TYPE IF EXISTS regulatoryregion")
    op.execute("DROP TYPE IF EXISTS allergendetectionlocation")
    op.execute("DROP TYPE IF EXISTS allergenflagstatus")
    op.execute("DROP TYPE IF EXISTS allergenflagseverity")