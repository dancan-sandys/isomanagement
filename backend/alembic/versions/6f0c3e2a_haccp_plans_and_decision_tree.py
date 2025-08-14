from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6f0c3e2a'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    # Add decision tree persistence columns to hazards
    with op.batch_alter_table('hazards') as batch_op:
        batch_op.add_column(sa.Column('decision_tree_steps', sa.Text()))
        batch_op.add_column(sa.Column('decision_tree_run_at', sa.DateTime(timezone=True)))
        batch_op.add_column(sa.Column('decision_tree_by', sa.Integer()))

    # Create HACCP plans table
    op.create_table(
        'haccp_plans',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('product_id', sa.Integer, nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('status', sa.Enum('draft', 'under_review', 'approved', 'obsolete', name='haccpplanstatus'), nullable=False, server_default='draft'),
        sa.Column('version', sa.String(20), nullable=False, server_default='1.0'),
        sa.Column('current_content', sa.Text),
        sa.Column('effective_date', sa.DateTime(timezone=True)),
        sa.Column('review_date', sa.DateTime(timezone=True)),
        sa.Column('approved_by', sa.Integer),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    # Create HACCP plan versions table
    op.create_table(
        'haccp_plan_versions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('plan_id', sa.Integer, nullable=False),
        sa.Column('version_number', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('change_description', sa.Text),
        sa.Column('change_reason', sa.Text),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('approved_by', sa.Integer),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )

    # Create HACCP plan approvals table
    op.create_table(
        'haccp_plan_approvals',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('plan_id', sa.Integer, nullable=False),
        sa.Column('approver_id', sa.Integer, nullable=False),
        sa.Column('approval_order', sa.Integer, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('comments', sa.Text),
        sa.Column('approved_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )


def downgrade():
    # Drop HACCP plan tables
    op.drop_table('haccp_plan_approvals')
    op.drop_table('haccp_plan_versions')
    op.drop_table('haccp_plans')
    # Drop enum type if created
    try:
        sa.Enum(name='haccpplanstatus').drop(op.get_bind(), checkfirst=True)
    except Exception:
        pass

    # Remove hazard columns
    with op.batch_alter_table('hazards') as batch_op:
        batch_op.drop_column('decision_tree_steps')
        batch_op.drop_column('decision_tree_run_at')
        batch_op.drop_column('decision_tree_by')


