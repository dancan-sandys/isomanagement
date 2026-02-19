from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Audit logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('resource_id', sa.String(100)),
        sa.Column('details', sa.JSON),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True))
    )

    # Document template versions
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

    # Document template approvals
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

    # Document distributions
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


def downgrade():
    op.drop_table('document_distributions')
    op.drop_table('document_template_approvals')
    op.drop_table('document_template_versions')
    op.drop_table('audit_logs')



