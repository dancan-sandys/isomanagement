"""add risk register tables and extend fields

Revision ID: a1b2c3d4e5f6
Revises: 312ee0729222
Create Date: 2025-08-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '312ee0729222'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in set(inspector.get_table_names())


def _column_exists(bind, table: str, column: str) -> bool:
    inspector = sa.inspect(bind)
    for col in inspector.get_columns(table):
        if col['name'] == column:
            return True
    return False


def upgrade() -> None:
    """Create risk tables if missing and extend enums/columns."""
    bind = op.get_bind()
    dialect = bind.dialect.name

    # Create enums with explicit names to ensure idempotence
    riskitemtype = sa.Enum('risk', 'opportunity', name='riskitemtype')
    riskcategory = sa.Enum(
        'process','supplier','staff','environment','haccp','prp','document','training','equipment','compliance','customer','other',
        name='riskcategory'
    )
    riskstatus = sa.Enum('open','monitoring','mitigated','closed', name='riskstatus')
    riskseverity = sa.Enum('low','medium','high','critical', name='riskseverity')
    risklikelihood = sa.Enum('rare','unlikely','possible','likely','almost_certain', name='risklikelihood')
    riskclassification = sa.Enum('food_safety','business','customer', name='riskclassification')
    riskdetectability = sa.Enum('easily_detectable','moderately_detectable','difficult','very_difficult','almost_undetectable', name='riskdetectability')

    # Ensure enum types exist (PostgreSQL); SQLite will ignore
    if dialect == 'postgresql':
        for enum_type in [riskitemtype, riskcategory, riskstatus, riskseverity, risklikelihood, riskclassification, riskdetectability]:
            try:
                enum_type.create(bind, checkfirst=True)
            except Exception:
                pass

    # Create risk_register
    if not _table_exists(bind, 'risk_register'):
        op.create_table(
            'risk_register',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('item_type', riskitemtype, nullable=False),
            sa.Column('risk_number', sa.String(length=50), nullable=False, unique=True, index=True),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('category', riskcategory, nullable=False, server_default='other'),
            sa.Column('classification', riskclassification, nullable=True),
            sa.Column('status', riskstatus, nullable=False, server_default='open'),
            sa.Column('severity', riskseverity, nullable=False, server_default='low'),
            sa.Column('likelihood', risklikelihood, nullable=False, server_default='unlikely'),
            sa.Column('detectability', riskdetectability, nullable=True),
            sa.Column('impact_score', sa.Integer()),
            sa.Column('risk_score', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('mitigation_plan', sa.Text()),
            sa.Column('residual_risk', sa.String(length=100)),
            sa.Column('assigned_to', sa.Integer()),
            sa.Column('due_date', sa.DateTime(timezone=True)),
            sa.Column('next_review_date', sa.DateTime(timezone=True)),
            sa.Column('references', sa.Text()),
            sa.Column('created_by', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True)),
        )

    # Create risk_actions
    if not _table_exists(bind, 'risk_actions'):
        op.create_table(
            'risk_actions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('item_id', sa.Integer, sa.ForeignKey('risk_register.id', ondelete='CASCADE'), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('assigned_to', sa.Integer()),
            sa.Column('due_date', sa.DateTime(timezone=True)),
            sa.Column('completed', sa.Boolean(), server_default=sa.text('0')),
            sa.Column('completed_at', sa.DateTime(timezone=True)),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        )

    # If tables already exist (e.g., previous partial migration), ensure columns are present
    if _table_exists(bind, 'risk_register'):
        if not _column_exists(bind, 'risk_register', 'classification'):
            op.add_column('risk_register', sa.Column('classification', riskclassification, nullable=True))
        if not _column_exists(bind, 'risk_register', 'detectability'):
            op.add_column('risk_register', sa.Column('detectability', riskdetectability, nullable=True))

        # Extend category enum for Postgres if missing values
        if dialect == 'postgresql':
            # Add values if not present
            try:
                op.execute("ALTER TYPE riskcategory ADD VALUE IF NOT EXISTS 'staff'")
            except Exception:
                pass
            try:
                op.execute("ALTER TYPE riskcategory ADD VALUE IF NOT EXISTS 'environment'")
            except Exception:
                pass


def downgrade() -> None:
    """Best-effort downgrade: drop added columns and tables (safe order)."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing = set(inspector.get_table_names())

    if 'risk_actions' in existing:
        op.drop_table('risk_actions')
    if 'risk_register' in existing:
        op.drop_table('risk_register')

    # Enum types removal is database-specific; skipping for safety


