"""merge_migration_heads

Revision ID: c134c1a76245
Revises: 004, 20250817_equipment_maintenance_expansions, b38d17d7bf76
Create Date: 2025-08-17 21:08:30.330621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c134c1a76245'
down_revision: Union[str, Sequence[str], None] = ('004', '20250817_equipment_maintenance_expansions', 'b38d17d7bf76')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
