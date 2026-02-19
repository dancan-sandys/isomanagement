"""add_hazard_analysis_fields

Revision ID: c12290b7f1b1
Revises: f1e2d3c4b5a6
Create Date: 2025-08-15 20:16:51.679130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c12290b7f1b1'
down_revision: Union[str, Sequence[str], None] = 'f1e2d3c4b5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new hazard analysis fields to hazards table
    op.add_column('hazards', sa.Column('rationale', sa.Text(), nullable=True))
    op.add_column('hazards', sa.Column('prp_reference_ids', sa.JSON(), nullable=True))
    op.add_column('hazards', sa.Column('references', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the added columns
    op.drop_column('hazards', 'references')
    op.drop_column('hazards', 'prp_reference_ids')
    op.drop_column('hazards', 'rationale')
