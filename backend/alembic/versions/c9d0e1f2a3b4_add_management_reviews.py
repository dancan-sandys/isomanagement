"""add management reviews tables

Revision ID: c9d0e1f2a3b4
Revises: b7c8d9e0f1a2
Create Date: 2025-08-12 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9d0e1f2a3b4'
down_revision: Union[str, Sequence[str], None] = 'b7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status_enum = sa.Enum('planned', 'in_progress', 'completed', name='managementreviewstatus')
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'management_reviews',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('attendees', sa.Text(), nullable=True),
        sa.Column('inputs', sa.Text(), nullable=True),
        sa.Column('outputs', sa.Text(), nullable=True),
        sa.Column('status', status_enum, nullable=False, server_default='planned'),
        sa.Column('next_review_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True)),
        sa.Column('updated_at', sa.DateTime(timezone=True)),
    )

    op.create_table(
        'review_agenda_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('review_id', sa.Integer(), sa.ForeignKey('management_reviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('topic', sa.String(length=200), nullable=False),
        sa.Column('discussion', sa.Text(), nullable=True),
        sa.Column('decision', sa.Text(), nullable=True),
        sa.Column('order_index', sa.Integer(), nullable=True),
    )

    op.create_table(
        'review_actions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('review_id', sa.Integer(), sa.ForeignKey('management_reviews.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assigned_to', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed', sa.Boolean(), server_default=sa.text('0'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True)),
    )


def downgrade() -> None:
    op.drop_table('review_actions')
    op.drop_table('review_agenda_items')
    op.drop_table('management_reviews')
    status_enum = sa.Enum(name='managementreviewstatus')
    status_enum.drop(op.get_bind(), checkfirst=True)


