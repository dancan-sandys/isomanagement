"""add missing document tables

Revision ID: 67e967ddfaf5
Revises: 0001
Create Date: 2025-08-11 11:29:34.053405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '67e967ddfaf5'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Create only the missing document-related tables, skipping any that already exist
    (e.g., when the app previously created tables via init_db()).
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # document_template_versions
    if 'document_template_versions' not in existing_tables:
        op.create_table(
            'document_template_versions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('template_id', sa.Integer, nullable=False),
            sa.Column('version_number', sa.String(20), nullable=False),
            sa.Column('template_file_path', sa.String(500)),
            sa.Column('template_content', sa.Text),
            sa.Column('change_description', sa.Text),
            sa.Column('created_by', sa.Integer, nullable=False),
            sa.Column('approved_by', sa.Integer),
            sa.Column('approved_at', sa.DateTime(timezone=True)),
            sa.Column('created_at', sa.DateTime(timezone=True))
        )

    # document_template_approvals
    if 'document_template_approvals' not in existing_tables:
        op.create_table(
            'document_template_approvals',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('template_id', sa.Integer, nullable=False),
            sa.Column('approver_id', sa.Integer, nullable=False),
            sa.Column('approval_order', sa.Integer, nullable=False),
            sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
            sa.Column('comments', sa.Text),
            sa.Column('approved_at', sa.DateTime(timezone=True)),
            sa.Column('created_at', sa.DateTime(timezone=True))
        )

    # document_distributions
    if 'document_distributions' not in existing_tables:
        op.create_table(
            'document_distributions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('document_id', sa.Integer, nullable=False),
            sa.Column('user_id', sa.Integer, nullable=False),
            sa.Column('copy_number', sa.String(50)),
            sa.Column('notes', sa.Text),
            sa.Column('distributed_at', sa.DateTime(timezone=True)),
            sa.Column('acknowledged_at', sa.DateTime(timezone=True))
        )


def downgrade() -> None:
    """Downgrade schema.

    Drop the document-related tables if they exist.
    """
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'document_distributions' in existing_tables:
        op.drop_table('document_distributions')
    if 'document_template_approvals' in existing_tables:
        op.drop_table('document_template_approvals')
    if 'document_template_versions' in existing_tables:
        op.drop_table('document_template_versions')
