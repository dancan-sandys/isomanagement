"""add_decision_tree_table

Revision ID: bd4abeadfe08
Revises: de1b4c3ce4a1
Create Date: 2025-08-16 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'bd4abeadfe08'
down_revision: Union[str, Sequence[str], None] = 'de1b4c3ce4a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create decision_trees table
    op.create_table('decision_trees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hazard_id', sa.Integer(), nullable=False),
        sa.Column('q1_answer', sa.Boolean(), nullable=False),
        sa.Column('q1_justification', sa.Text(), nullable=True),
        sa.Column('q1_answered_by', sa.Integer(), nullable=True),
        sa.Column('q1_answered_at', sa.DateTime(), nullable=True),
        sa.Column('q2_answer', sa.Boolean(), nullable=True),
        sa.Column('q2_justification', sa.Text(), nullable=True),
        sa.Column('q2_answered_by', sa.Integer(), nullable=True),
        sa.Column('q2_answered_at', sa.DateTime(), nullable=True),
        sa.Column('q3_answer', sa.Boolean(), nullable=True),
        sa.Column('q3_justification', sa.Text(), nullable=True),
        sa.Column('q3_answered_by', sa.Integer(), nullable=True),
        sa.Column('q3_answered_at', sa.DateTime(), nullable=True),
        sa.Column('q4_answer', sa.Boolean(), nullable=True),
        sa.Column('q4_justification', sa.Text(), nullable=True),
        sa.Column('q4_answered_by', sa.Integer(), nullable=True),
        sa.Column('q4_answered_at', sa.DateTime(), nullable=True),
        sa.Column('is_ccp', sa.Boolean(), nullable=True),
        sa.Column('decision_reasoning', sa.Text(), nullable=True),
        sa.Column('decision_date', sa.DateTime(), nullable=True),
        sa.Column('decision_by', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['hazard_id'], ['hazards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['q1_answered_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['q2_answered_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['q3_answered_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['q4_answered_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['decision_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('hazard_id')
    )
    op.create_index(op.f('ix_decision_trees_id'), 'decision_trees', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_decision_trees_id'), table_name='decision_trees')
    op.drop_table('decision_trees')
