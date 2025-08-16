"""merge traceability enhancements with existing head

Revision ID: 81da6fc134d5
Revises: ecfb85dde236, h3f4e5d6c7a8
Create Date: 2025-08-16 14:46:31.131286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81da6fc134d5'
down_revision: Union[str, Sequence[str], None] = ('ecfb85dde236', 'h3f4e5d6c7a8')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
