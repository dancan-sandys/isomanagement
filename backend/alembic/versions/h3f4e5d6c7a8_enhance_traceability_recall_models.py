"""Enhance traceability and recall management models for ISO 22005:2007 and ISO 22000:2018 compliance

Revision ID: h3f4e5d6c7a8
Revises: g2f3e4d5c6a7
Create Date: 2025-01-27 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'h3f4e5d6c7a8'
down_revision: Union[str, Sequence[str], None] = 'g2f3e4d5c6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create traceability_nodes table
    op.create_table(
        'traceability_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(50), nullable=False),
        sa.Column('node_level', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(50), nullable=False),
        sa.Column('ccp_related', sa.Boolean(), default=False),
        sa.Column('ccp_id', sa.Integer(), nullable=True),
        sa.Column('verification_required', sa.Boolean(), default=True),
        sa.Column('verification_status', sa.String(20), default='pending'),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id']),
        sa.ForeignKeyConstraint(['ccp_id'], ['ccps.id']),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create recall_classifications table
    op.create_table(
        'recall_classifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recall_id', sa.Integer(), nullable=False),
        sa.Column('health_risk_level', sa.String(20), nullable=False),
        sa.Column('affected_population', sa.Text(), nullable=True),
        sa.Column('exposure_route', sa.String(50), nullable=True),
        sa.Column('severity_assessment', sa.Text(), nullable=True),
        sa.Column('probability_assessment', sa.Text(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('classification_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('classified_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['recall_id'], ['recalls.id']),
        sa.ForeignKeyConstraint(['classified_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create recall_communications table
    op.create_table(
        'recall_communications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recall_id', sa.Integer(), nullable=False),
        sa.Column('stakeholder_type', sa.String(50), nullable=False),
        sa.Column('communication_method', sa.String(50), nullable=False),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('sent_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_by', sa.Integer(), nullable=True),
        sa.Column('confirmation_received', sa.Boolean(), default=False),
        sa.Column('response_time', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['recall_id'], ['recalls.id']),
        sa.ForeignKeyConstraint(['sent_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create recall_effectiveness table
    op.create_table(
        'recall_effectiveness',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recall_id', sa.Integer(), nullable=False),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('quantity_recalled_percentage', sa.Float(), nullable=False),
        sa.Column('time_to_complete', sa.Integer(), nullable=True),
        sa.Column('customer_response_rate', sa.Float(), nullable=True),
        sa.Column('product_recovery_rate', sa.Float(), nullable=True),
        sa.Column('effectiveness_score', sa.Integer(), nullable=True),
        sa.Column('lessons_learned', sa.Text(), nullable=True),
        sa.Column('improvement_actions', sa.Text(), nullable=True),
        sa.Column('verified_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['recall_id'], ['recalls.id']),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add GS1-compliant identification fields to batches table
    op.add_column('batches', sa.Column('gtin', sa.String(14), nullable=True))
    op.add_column('batches', sa.Column('sscc', sa.String(18), nullable=True))
    op.add_column('batches', sa.Column('hierarchical_lot_number', sa.String(50), nullable=True))
    
    # Add enhanced traceability fields to batches table
    op.add_column('batches', sa.Column('supplier_information', sa.JSON(), nullable=True))
    op.add_column('batches', sa.Column('customer_information', sa.JSON(), nullable=True))
    op.add_column('batches', sa.Column('distribution_location', sa.String(100), nullable=True))
    
    # Update existing parent_batches and child_batches columns to JSON type
    # Note: SQLite doesn't support ALTER COLUMN TYPE, so we'll need to handle this differently
    # For now, we'll keep them as Text and handle JSON conversion in the application layer
    
    # Create indexes for performance optimization
    op.create_index('ix_traceability_nodes_batch_id', 'traceability_nodes', ['batch_id'])
    op.create_index('ix_traceability_nodes_node_type', 'traceability_nodes', ['node_type'])
    op.create_index('ix_traceability_nodes_ccp_related', 'traceability_nodes', ['ccp_related'])
    op.create_index('ix_recall_classifications_recall_id', 'recall_classifications', ['recall_id'])
    op.create_index('ix_recall_classifications_health_risk_level', 'recall_classifications', ['health_risk_level'])
    op.create_index('ix_recall_communications_recall_id', 'recall_communications', ['recall_id'])
    op.create_index('ix_recall_communications_stakeholder_type', 'recall_communications', ['stakeholder_type'])
    op.create_index('ix_recall_effectiveness_recall_id', 'recall_effectiveness', ['recall_id'])
    op.create_index('ix_batches_gtin', 'batches', ['gtin'])
    op.create_index('ix_batches_sscc', 'batches', ['sscc'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_batches_sscc', 'batches')
    op.drop_index('ix_batches_gtin', 'batches')
    op.drop_index('ix_recall_effectiveness_recall_id', 'recall_effectiveness')
    op.drop_index('ix_recall_communications_stakeholder_type', 'recall_communications')
    op.drop_index('ix_recall_communications_recall_id', 'recall_communications')
    op.drop_index('ix_recall_classifications_health_risk_level', 'recall_classifications')
    op.drop_index('ix_recall_classifications_recall_id', 'recall_classifications')
    op.drop_index('ix_traceability_nodes_ccp_related', 'traceability_nodes')
    op.drop_index('ix_traceability_nodes_node_type', 'traceability_nodes')
    op.drop_index('ix_traceability_nodes_batch_id', 'traceability_nodes')
    
    # Drop columns from batches table
    op.drop_column('batches', 'distribution_location')
    op.drop_column('batches', 'customer_information')
    op.drop_column('batches', 'supplier_information')
    op.drop_column('batches', 'hierarchical_lot_number')
    op.drop_column('batches', 'sscc')
    op.drop_column('batches', 'gtin')
    
    # Drop tables
    op.drop_table('recall_effectiveness')
    op.drop_table('recall_communications')
    op.drop_table('recall_classifications')
    op.drop_table('traceability_nodes')
