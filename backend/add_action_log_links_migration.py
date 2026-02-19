#!/usr/bin/env python3
"""
Database Migration: Add action_log_id to multiple action tables
This links various module actions to the central actions log system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.database import DATABASE_URL

def run_migration():
    """Add action_log_id columns to multiple action tables"""
    engine = create_engine(DATABASE_URL)
    
    # Tables and their corresponding action_log_id columns to add
    tables_to_update = [
        "review_actions",  # Management Review (already exists)
        "capa_actions",    # Non-Conformance CAPA Actions
        "immediate_actions", # Non-Conformance Immediate Actions  
        "preventive_actions", # Non-Conformance Preventive Actions
        "risk_actions",    # Risk Management Actions
        "audit_findings",  # Audit Findings
        "prp_corrective_actions", # PRP Corrective Actions
        "prp_preventive_actions", # PRP Preventive Actions
        "complaints",      # Complaint resolutions
        "recall_actions",  # Recall Actions
        "training_records", # Training Actions (if table exists)
        "supplier_evaluations", # Supplier Actions (if table exists)
        "haccp_monitoring_records", # HACCP Actions (if table exists)
    ]
    
    try:
        with engine.connect() as conn:
            for table_name in tables_to_update:
                # Check if table exists
                table_exists = conn.execute(text(f"""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_name='{table_name}'
                """)).fetchone()
                
                if not table_exists:
                    print(f"⚠️  Table {table_name} does not exist, skipping...")
                    continue
                
                # Check if column already exists
                result = conn.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='{table_name}' AND column_name='action_log_id'
                """))
                
                if result.fetchone():
                    print(f"✅ action_log_id column already exists in {table_name} table")
                    continue
                
                # Add the action_log_id column
                conn.execute(text(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN action_log_id INTEGER,
                    ADD CONSTRAINT fk_{table_name}_action_log_id 
                    FOREIGN KEY (action_log_id) REFERENCES action_logs(id)
                """))
                
                # Add index for better performance
                conn.execute(text(f"""
                    CREATE INDEX idx_{table_name}_action_log_id 
                    ON {table_name}(action_log_id)
                """))
                
                print(f"✅ Successfully added action_log_id column to {table_name} table")
            
            conn.commit()
            print("✅ Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    print("🔄 Running migration: Add action_log_id to multiple action tables...")
    run_migration()