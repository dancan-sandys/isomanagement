"""add audit kpi fields

Revision ID: e1f2a3b4c5d6
Revises: d0f1e2a3b4c5
Create Date: 2025-08-15 12:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f2a3b4c5d6'
down_revision: Union[str, Sequence[str], None] = 'd0f1e2a3b4c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Add audits.actual_end_at
    if 'audits' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('audits')}
        if 'actual_end_at' not in cols:
            op.add_column('audits', sa.Column('actual_end_at', sa.DateTime(), nullable=True))

    # Add audit_findings.finding_type enum and column
    if 'audit_findings' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('audit_findings')}
        if 'finding_type' not in cols:
            # Create enum type if not exists (no-op on SQLite)
            findingtype = sa.Enum('nonconformity', 'observation', 'ofi', name='findingtype')
            try:
                findingtype.create(bind, checkfirst=True)
            except Exception:
                pass
            # On SQLite, avoid ALTER to drop default; add without server_default where possible
            if bind.dialect.name == 'sqlite':
                op.add_column('audit_findings', sa.Column('finding_type', sa.String(length=32), nullable=True))
                # Set default value for existing rows via UPDATE
                op.execute("UPDATE audit_findings SET finding_type = 'nonconformity' WHERE finding_type IS NULL")
                # Make column non-nullable afterwards using batch alter if needed
                with op.batch_alter_table('audit_findings') as batch_op:
                    batch_op.alter_column('finding_type', existing_type=sa.String(length=32), nullable=False)
            else:
                op.add_column('audit_findings', sa.Column('finding_type', findingtype, nullable=False, server_default='nonconformity'))
                op.alter_column('audit_findings', 'finding_type', server_default=None)

        if 'closed_at' not in cols:
            op.add_column('audit_findings', sa.Column('closed_at', sa.DateTime(), nullable=True))

    # Note: audit_plans.approved_at will be added when AuditPlan table is introduced


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if 'audit_findings' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('audit_findings')}
        if 'closed_at' in cols:
            op.drop_column('audit_findings', 'closed_at')
        if 'finding_type' in cols:
            op.drop_column('audit_findings', 'finding_type')
            # Drop enum type
            findingtype = sa.Enum('nonconformity', 'observation', 'ofi', name='findingtype')
            findingtype.drop(bind, checkfirst=True)

    if 'audits' in inspector.get_table_names():
        cols = {c['name'] for c in inspector.get_columns('audits')}
        if 'actual_end_at' in cols:
            op.drop_column('audits', 'actual_end_at')


