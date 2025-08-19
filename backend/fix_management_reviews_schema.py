#!/usr/bin/env python3
"""
Management Reviews Schema Fix
Fix all missing columns in the Management Reviews module
"""

import sqlite3
import sys

def fix_management_reviews_schema():
    """Fix all missing columns in Management Reviews module"""
    print("🔧 Management Reviews Schema Fix")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # 1. Fix management_reviews table
        print("\n📋 Fixing management_reviews table...")
        cursor.execute("PRAGMA table_info(management_reviews)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        missing_columns = [
            ("review_type", "VARCHAR(50)"),
            ("review_scope", "TEXT"),
            ("chairperson_id", "INTEGER"),
            ("food_safety_policy_reviewed", "BOOLEAN DEFAULT FALSE"),
            ("food_safety_objectives_reviewed", "BOOLEAN DEFAULT FALSE"),
            ("fsms_changes_required", "BOOLEAN DEFAULT FALSE"),
            ("resource_adequacy_assessment", "TEXT"),
            ("improvement_opportunities", "TEXT"),
            ("previous_actions_status", "TEXT"),
            ("external_issues", "TEXT"),
            ("internal_issues", "TEXT"),
            ("customer_feedback_summary", "TEXT"),
            ("supplier_performance_summary", "TEXT"),
            ("audit_results_summary", "TEXT"),
            ("nc_capa_summary", "TEXT"),
            ("kpi_performance_summary", "TEXT"),
            ("minutes", "TEXT"),
            ("review_effectiveness_score", "INTEGER"),
            ("effectiveness_justification", "TEXT"),
            ("review_frequency", "VARCHAR(100)"),
            ("completed_at", "DATETIME")
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE management_reviews ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # 2. Fix review_actions table
        print("\n📋 Fixing review_actions table...")
        cursor.execute("PRAGMA table_info(review_actions)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        missing_columns = [
            ("action_type", "VARCHAR(50)"),
            ("priority", "VARCHAR(20)"),
            ("status", "VARCHAR(20)"),
            ("progress_percentage", "INTEGER DEFAULT 0"),
            ("progress_notes", "TEXT"),
            ("completed_by", "INTEGER"),
            ("verification_required", "BOOLEAN DEFAULT FALSE"),
            ("verified", "BOOLEAN DEFAULT FALSE"),
            ("verified_at", "DATETIME"),
            ("verified_by", "INTEGER"),
            ("verification_notes", "TEXT"),
            ("estimated_effort_hours", "FLOAT"),
            ("actual_effort_hours", "FLOAT"),
            ("resource_requirements", "TEXT"),
            ("updated_at", "DATETIME")
        ]
        
        for column_name, column_type in missing_columns:
            if column_name not in existing_columns:
                cursor.execute(f"ALTER TABLE review_actions ADD COLUMN {column_name} {column_type}")
                print(f"✅ Added column: {column_name} ({column_type})")
            else:
                print(f"⚠️  Column already exists: {column_name}")
        
        # 3. Create performance indexes
        print("\n📊 Creating performance indexes...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_management_reviews_status ON management_reviews(status)",
            "CREATE INDEX IF NOT EXISTS idx_management_reviews_review_date ON management_reviews(review_date)",
            "CREATE INDEX IF NOT EXISTS idx_management_reviews_review_type ON management_reviews(review_type)",
            "CREATE INDEX IF NOT EXISTS idx_review_actions_review_id ON review_actions(review_id)",
            "CREATE INDEX IF NOT EXISTS idx_review_actions_status ON review_actions(status)",
            "CREATE INDEX IF NOT EXISTS idx_review_actions_due_date ON review_actions(due_date)",
            "CREATE INDEX IF NOT EXISTS idx_review_actions_completed ON review_actions(completed)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            print(f"✅ Created index: {index_sql.split('IF NOT EXISTS ')[1].split(' ON ')[0]}")
        
        # 4. Test the fixes
        print("\n📋 Testing the fixes...")
        
        # Test inserting a management review
        try:
            cursor.execute("""
                INSERT INTO management_reviews 
                (title, review_date, review_type, review_scope, attendees, status, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, ('Test Review', '2025-08-19', 'SCHEDULED', 'Test scope', '[]', 'PLANNED', 12))
            
            # Get the inserted ID
            test_id = cursor.lastrowid
            
            # Clean up the test record
            cursor.execute("DELETE FROM management_reviews WHERE id = ?", (test_id,))
            
            print("✅ Management review creation test passed")
        except Exception as e:
            print(f"❌ Management review creation test failed: {str(e)}")
            return False
        
        # Test inserting a review action
        try:
            cursor.execute("""
                INSERT INTO review_actions 
                (review_id, title, description, assigned_to, due_date, action_type, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (1, 'Test Action', 'Test description', 12, '2025-12-31', 'CORRECTIVE', 'OPEN'))
            
            # Get the inserted ID
            test_id = cursor.lastrowid
            
            # Clean up the test record
            cursor.execute("DELETE FROM review_actions WHERE id = ?", (test_id,))
            
            print("✅ Review action creation test passed")
        except Exception as e:
            print(f"❌ Review action creation test failed: {str(e)}")
            return False
        
        conn.commit()
        print("\n✅ Management Reviews schema fixes completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing Management Reviews schema: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = fix_management_reviews_schema()
    sys.exit(0 if success else 1)
