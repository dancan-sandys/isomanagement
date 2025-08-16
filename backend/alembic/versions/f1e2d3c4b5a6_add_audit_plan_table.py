"""add audit_plans table

Revision ID: f1e2d3c4b5a6
Revises: 0d44dfbaf319
Create Date: 2025-08-15 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1e2d3c4b5a6'
down_revision: Union[str, Sequence[str], None] = '0d44dfbaf319'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'audit_plans' not in inspector.get_table_names():
        op.create_table(
            'audit_plans',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('audit_id', sa.Integer, sa.ForeignKey('audits.id', ondelete='CASCADE'), nullable=False, unique=True),
            sa.Column('agenda', sa.Text()),
            sa.Column('criteria_refs', sa.Text()),
            sa.Column('sampling_plan', sa.Text()),
            sa.Column('documents_to_review', sa.Text()),
            sa.Column('logistics', sa.Text()),
            sa.Column('approved_by', sa.Integer()),
            sa.Column('approved_at', sa.DateTime()),
            sa.Column('created_at', sa.DateTime()),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'audit_plans' in inspector.get_table_names():
        op.drop_table('audit_plans')


