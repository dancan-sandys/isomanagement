"""add allergen and label control tables

Revision ID: 6b1f4a2a1abc
Revises: 312ee0729222
Create Date: 2025-08-12 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b1f4a2a1abc'
down_revision: Union[str, Sequence[str], None] = '312ee0729222'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if 'product_allergen_assessments' not in existing:
        op.create_table(
            'product_allergen_assessments',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
            sa.Column('inherent_allergens', sa.Text()),
            sa.Column('cross_contact_sources', sa.Text()),
            sa.Column('risk_level', sa.Enum('low', 'medium', 'high', name='allergenrisklevel'), nullable=False),
            sa.Column('precautionary_labeling', sa.String(length=255)),
            sa.Column('control_measures', sa.Text()),
            sa.Column('validation_verification', sa.Text()),
            sa.Column('reviewed_by', sa.Integer()),
            sa.Column('last_reviewed_at', sa.DateTime()),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime()),
            sa.Column('updated_at', sa.DateTime()),
        )

    if 'label_templates' not in existing:
        op.create_table(
            'label_templates',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id', ondelete='SET NULL')),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('1')),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime()),
        )

    if 'label_template_versions' not in existing:
        op.create_table(
            'label_template_versions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('template_id', sa.Integer, sa.ForeignKey('label_templates.id', ondelete='CASCADE'), nullable=False),
            sa.Column('version_number', sa.Integer, nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('change_description', sa.Text()),
            sa.Column('change_reason', sa.Text()),
            sa.Column('status', sa.Enum('draft', 'under_review', 'approved', 'rejected', name='labelversionstatus'), nullable=False),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime()),
        )

    if 'label_template_approvals' not in existing:
        op.create_table(
            'label_template_approvals',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('version_id', sa.Integer, sa.ForeignKey('label_template_versions.id', ondelete='CASCADE'), nullable=False),
            sa.Column('approver_id', sa.Integer(), nullable=False),
            sa.Column('approval_order', sa.Integer(), nullable=False),
            sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='labelapprovalstatus'), nullable=False),
            sa.Column('comments', sa.Text()),
            sa.Column('decided_at', sa.DateTime()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if 'label_template_approvals' in existing:
        op.drop_table('label_template_approvals')
    if 'label_template_versions' in existing:
        op.drop_table('label_template_versions')
    if 'label_templates' in existing:
        op.drop_table('label_templates')
    if 'product_allergen_assessments' in existing:
        op.drop_table('product_allergen_assessments')
    # Enum cleanup omitted for idempotency


