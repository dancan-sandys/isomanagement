"""merge heads for management review enhancement

Revision ID: b796ce557432
Revises: 20250117_enhanced_allergen_control, c134c1a76245, enhance_mgmt_reviews_iso
Create Date: 2025-08-18 05:25:21.479403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b796ce557432'
down_revision: Union[str, Sequence[str], None] = ('20250117_enhanced_allergen_control', 'c134c1a76245', 'enhance_mgmt_reviews_iso')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
