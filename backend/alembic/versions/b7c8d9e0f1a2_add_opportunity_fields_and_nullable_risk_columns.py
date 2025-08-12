"""add opportunity fields and relax risk columns for opportunities

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2025-08-12 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('risk_register') as batch_op:
        # New opportunity fields
        batch_op.add_column(sa.Column('opportunity_benefit', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('opportunity_feasibility', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('opportunity_score', sa.Integer(), nullable=True))
        # Relax severity/likelihood to nullable for opportunities
        batch_op.alter_column('severity', existing_type=sa.Enum('low','medium','high','critical', name='riskseverity'), nullable=True)
        batch_op.alter_column('likelihood', existing_type=sa.Enum('rare','unlikely','possible','likely','almost_certain', name='risklikelihood'), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('risk_register') as batch_op:
        # Revert nullability
        batch_op.alter_column('likelihood', existing_type=sa.Enum('rare','unlikely','possible','likely','almost_certain', name='risklikelihood'), nullable=False)
        batch_op.alter_column('severity', existing_type=sa.Enum('low','medium','high','critical', name='riskseverity'), nullable=False)
        # Drop opportunity fields
        batch_op.drop_column('opportunity_score')
        batch_op.drop_column('opportunity_feasibility')
        batch_op.drop_column('opportunity_benefit')


