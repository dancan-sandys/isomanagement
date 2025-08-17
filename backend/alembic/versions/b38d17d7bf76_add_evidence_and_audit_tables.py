"""add evidence and audit tables

Revision ID: b38d17d7bf76
Revises: 266858443ad8
Create Date: 2024-12-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'b38d17d7bf76'
down_revision = '266858443ad8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create haccp_evidence_attachments table
    op.create_table('haccp_evidence_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('record_type', sa.String(length=50), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('evidence_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('upload_date', sa.DateTime(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_haccp_evidence_attachments_id'), 'haccp_evidence_attachments', ['id'], unique=False)
    
    # Create haccp_audit_logs table
    op.create_table('haccp_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_description', sa.Text(), nullable=False),
        sa.Column('record_type', sa.String(length=50), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_role', sa.String(length=50), nullable=True),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        sa.Column('changed_fields', sa.Text(), nullable=True),
        sa.Column('signature_hash', sa.String(length=255), nullable=True),
        sa.Column('signature_timestamp', sa.DateTime(), nullable=True),
        sa.Column('signature_method', sa.String(length=50), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('session_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_haccp_audit_logs_id'), 'haccp_audit_logs', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_haccp_audit_logs_id'), table_name='haccp_audit_logs')
    op.drop_table('haccp_audit_logs')
    op.drop_index(op.f('ix_haccp_evidence_attachments_id'), table_name='haccp_evidence_attachments')
    op.drop_table('haccp_evidence_attachments')
