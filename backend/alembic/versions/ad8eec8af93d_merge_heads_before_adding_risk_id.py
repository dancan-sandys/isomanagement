"""merge_heads_before_adding_risk_id

Revision ID: ad8eec8af93d
Revises: add_action_log_id_to_ccp_monitoring_logs, b796ce557432
Create Date: 2025-08-27 21:55:30.999366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad8eec8af93d'
down_revision: Union[str, Sequence[str], None] = ('add_action_log_id_to_ccp_monitoring_logs', 'b796ce557432')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
