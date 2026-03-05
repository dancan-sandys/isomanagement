"""Merge heads: add_haccp_verification_records and 2a3bd4897b81

Revision ID: merge_haccp_verification_heads
Revises: add_haccp_verification_records, 2a3bd4897b81
Create Date: 2025-03-04

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'merge_haccp_verification_heads'
down_revision: Union[str, Sequence[str], None] = ('add_haccp_verification_records', '2a3bd4897b81')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
