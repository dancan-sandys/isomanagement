"""add haccp_required_trainings table and enums

Revision ID: 81a2b3c4d5e6
Revises: 6f0c3e2a_haccp_plans_and_decision_tree
Create Date: 2025-08-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81a2b3c4d5e6'
down_revision = '6f0c3e2a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum type for TrainingAction
    trainingaction = sa.Enum('monitor', 'verify', name='trainingaction')
    trainingaction.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'haccp_required_trainings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('action', trainingaction, nullable=False),
        sa.Column('ccp_id', sa.Integer(), nullable=True),
        sa.Column('equipment_id', sa.Integer(), nullable=True),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Foreign keys (use ondelete semantics aligned with models)
    op.create_foreign_key(
        'fk_haccp_req_tr_role',
        'haccp_required_trainings', 'roles', ['role_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_haccp_req_tr_ccp',
        'haccp_required_trainings', 'ccps', ['ccp_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'fk_haccp_req_tr_equipment',
        'haccp_required_trainings', 'equipment', ['equipment_id'], ['id'], ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_haccp_req_tr_program',
        'haccp_required_trainings', 'training_programs', ['program_id'], ['id'], ondelete='CASCADE'
    )

    # Indexes helpful for lookups
    op.create_index('ix_haccp_req_tr_role_action', 'haccp_required_trainings', ['role_id', 'action'])
    op.create_index('ix_haccp_req_tr_ccp', 'haccp_required_trainings', ['ccp_id'])
    op.create_index('ix_haccp_req_tr_equipment', 'haccp_required_trainings', ['equipment_id'])


def downgrade() -> None:
    op.drop_index('ix_haccp_req_tr_equipment', table_name='haccp_required_trainings')
    op.drop_index('ix_haccp_req_tr_ccp', table_name='haccp_required_trainings')
    op.drop_index('ix_haccp_req_tr_role_action', table_name='haccp_required_trainings')
    op.drop_constraint('fk_haccp_req_tr_program', 'haccp_required_trainings', type_='foreignkey')
    op.drop_constraint('fk_haccp_req_tr_equipment', 'haccp_required_trainings', type_='foreignkey')
    op.drop_constraint('fk_haccp_req_tr_ccp', 'haccp_required_trainings', type_='foreignkey')
    op.drop_constraint('fk_haccp_req_tr_role', 'haccp_required_trainings', type_='foreignkey')
    op.drop_table('haccp_required_trainings')

    # Drop enum type
    trainingaction = sa.Enum('monitor', 'verify', name='trainingaction')
    trainingaction.drop(op.get_bind(), checkfirst=True)


