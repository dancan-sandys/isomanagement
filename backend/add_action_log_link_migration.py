#!/usr/bin/env python3
"""
Database Migration: Add action_log_id to review_actions table
This links management review actions to the central actions log system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.database import DATABASE_URL, get_db
from app.models.management_review import ReviewAction
from app.models.actions_log import ActionLog

def run_migration():
    """Add action_log_id column to review_actions table"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='review_actions' AND column_name='action_log_id'
            """))
            
            if result.fetchone():
                print("✅ action_log_id column already exists in review_actions table")
                return
            
            # Add the action_log_id column
            conn.execute(text("""
                ALTER TABLE review_actions 
                ADD COLUMN action_log_id INTEGER,
                ADD CONSTRAINT fk_review_actions_action_log_id 
                FOREIGN KEY (action_log_id) REFERENCES action_logs(id)
            """))
            
            # Add index for better performance
            conn.execute(text("""
                CREATE INDEX idx_review_actions_action_log_id 
                ON review_actions(action_log_id)
            """))
            
            conn.commit()
            print("✅ Successfully added action_log_id column to review_actions table")
            print("✅ Added foreign key constraint to action_logs table")
            print("✅ Added index for action_log_id column")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    print("🔄 Running migration: Add action_log_id to review_actions...")
    run_migration()
    print("✅ Migration completed successfully!")