"""add audit management tables

Revision ID: 312ee0729222
Revises: 67e967ddfaf5
Create Date: 2025-08-11 14:51:32.986183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '312ee0729222'
down_revision: Union[str, Sequence[str], None] = '67e967ddfaf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: create audit management tables if missing."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if 'audits' not in existing:
        op.create_table(
            'audits',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('audit_type', sa.Enum('internal', 'external', 'supplier', name='audittype'), nullable=False),
            sa.Column('scope', sa.Text()),
            sa.Column('objectives', sa.Text()),
            sa.Column('criteria', sa.Text()),
            sa.Column('start_date', sa.DateTime()),
            sa.Column('end_date', sa.DateTime()),
            sa.Column('status', sa.Enum('planned', 'in_progress', 'completed', 'closed', name='auditstatus'), nullable=False),
            sa.Column('auditor_id', sa.Integer()),
            sa.Column('lead_auditor_id', sa.Integer()),
            sa.Column('auditee_department', sa.String(length=255)),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime()),
            sa.Column('updated_at', sa.DateTime()),
        )

    if 'audit_checklist_templates' not in existing:
        op.create_table(
            'audit_checklist_templates',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(length=255), nullable=False),
            sa.Column('clause_ref', sa.String(length=100)),
            sa.Column('question', sa.Text(), nullable=False),
            sa.Column('requirement', sa.Text()),
            sa.Column('category', sa.String(length=100)),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('1')),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime()),
        )

    if 'audit_checklist_items' not in existing:
        op.create_table(
            'audit_checklist_items',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('audit_id', sa.Integer, sa.ForeignKey('audits.id', ondelete='CASCADE'), nullable=False),
            sa.Column('template_id', sa.Integer),
            sa.Column('clause_ref', sa.String(length=100)),
            sa.Column('question', sa.Text()),
            sa.Column('response', sa.Enum('conforming', 'nonconforming', 'not_applicable', name='checklistresponse')),
            sa.Column('evidence_text', sa.Text()),
            sa.Column('score', sa.Float()),
            sa.Column('comment', sa.Text()),
            sa.Column('evidence_file_path', sa.String(length=500)),
            sa.Column('responsible_person_id', sa.Integer()),
            sa.Column('due_date', sa.DateTime()),
            sa.Column('created_at', sa.DateTime()),
        )

    if 'audit_findings' not in existing:
        op.create_table(
            'audit_findings',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('audit_id', sa.Integer, sa.ForeignKey('audits.id', ondelete='CASCADE'), nullable=False),
            sa.Column('clause_ref', sa.String(length=100)),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('severity', sa.Enum('minor', 'major', 'critical', name='findingseverity'), nullable=False),
            sa.Column('corrective_action', sa.Text()),
            sa.Column('responsible_person_id', sa.Integer()),
            sa.Column('target_completion_date', sa.DateTime()),
            sa.Column('status', sa.Enum('open', 'in_progress', 'verified', 'closed', name='findingstatus'), nullable=False),
            sa.Column('related_nc_id', sa.Integer()),
            sa.Column('created_at', sa.DateTime()),
        )

    if 'audit_attachments' not in existing:
        op.create_table(
            'audit_attachments',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('audit_id', sa.Integer, sa.ForeignKey('audits.id', ondelete='CASCADE'), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('uploaded_by', sa.Integer(), nullable=False),
            sa.Column('uploaded_at', sa.DateTime()),
        )

    if 'audit_item_attachments' not in existing:
        op.create_table(
            'audit_item_attachments',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('item_id', sa.Integer, sa.ForeignKey('audit_checklist_items.id', ondelete='CASCADE'), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('uploaded_by', sa.Integer(), nullable=False),
            sa.Column('uploaded_at', sa.DateTime()),
        )

    if 'audit_finding_attachments' not in existing:
        op.create_table(
            'audit_finding_attachments',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('finding_id', sa.Integer, sa.ForeignKey('audit_findings.id', ondelete='CASCADE'), nullable=False),
            sa.Column('file_path', sa.String(length=500), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('uploaded_by', sa.Integer(), nullable=False),
            sa.Column('uploaded_at', sa.DateTime()),
        )

    if 'audit_auditees' not in existing:
        op.create_table(
            'audit_auditees',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('audit_id', sa.Integer, sa.ForeignKey('audits.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.String(length=100)),
            sa.Column('added_at', sa.DateTime()),
        )


def downgrade() -> None:
    """Downgrade schema: drop audit management tables if they exist."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if 'audit_attachments' in existing:
        op.drop_table('audit_attachments')
    if 'audit_findings' in existing:
        op.drop_table('audit_findings')
    if 'audit_checklist_items' in existing:
        op.drop_table('audit_checklist_items')
    if 'audit_checklist_templates' in existing:
        op.drop_table('audit_checklist_templates')
    if 'audits' in existing:
        op.drop_table('audits')
    # Enum drops are vendor-specific; skip for idempotency
