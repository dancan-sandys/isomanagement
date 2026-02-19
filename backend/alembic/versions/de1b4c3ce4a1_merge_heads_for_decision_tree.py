"""merge_heads_for_decision_tree

Revision ID: de1b4c3ce4a1
Revises: ecfb85dde236, g2f3e4d5c6a7
Create Date: 2025-08-16 13:35:57.554938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de1b4c3ce4a1'
down_revision: Union[str, Sequence[str], None] = ('ecfb85dde236', 'g2f3e4d5c6a7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
