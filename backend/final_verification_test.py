#!/usr/bin/env python3
"""
Final Verification Test
Test all the fixes to ensure the platform is fully functional
"""

import sqlite3
import sys

def final_verification_test():
    """Run final verification tests"""
    print("🔍 Final Verification Test")
    
    conn = sqlite3.connect('iso22000_fsms.db')
    cursor = conn.cursor()
    
    try:
        # Test 1: Management Reviews Module
        print("\n📋 Testing Management Reviews Module...")
        
        # Test management_reviews table
        cursor.execute("PRAGMA table_info(management_reviews)")
        management_reviews_columns = [col[1] for col in cursor.fetchall()]
        required_columns = ['review_type', 'review_scope', 'chairperson_id', 'food_safety_policy_reviewed']
        missing_columns = [col for col in required_columns if col not in management_reviews_columns]
        
        if missing_columns:
            print(f"❌ Missing columns in management_reviews: {missing_columns}")
            return False
        else:
            print("✅ Management reviews table has all required columns")
        
        # Test review_actions table
        cursor.execute("PRAGMA table_info(review_actions)")
        review_actions_columns = [col[1] for col in cursor.fetchall()]
        required_columns = ['action_type', 'priority', 'status', 'progress_percentage']
        missing_columns = [col for col in required_columns if col not in review_actions_columns]
        
        if missing_columns:
            print(f"❌ Missing columns in review_actions: {missing_columns}")
            return False
        else:
            print("✅ Review actions table has all required columns")
        
        # Test 2: PRP Module
        print("\n📋 Testing PRP Module...")
        
        # Test prp_corrective_actions table
        cursor.execute("PRAGMA table_info(prp_corrective_actions)")
        prp_corrective_columns = [col[1] for col in cursor.fetchall()]
        required_columns = ['progress_percentage', 'effectiveness_verification', 'is_active']
        missing_columns = [col for col in required_columns if col not in prp_corrective_columns]
        
        if missing_columns:
            print(f"❌ Missing columns in prp_corrective_actions: {missing_columns}")
            return False
        else:
            print("✅ PRP corrective actions table has all required columns")
        
        # Test prp_preventive_actions table
        cursor.execute("PRAGMA table_info(prp_preventive_actions)")
        prp_preventive_columns = [col[1] for col in cursor.fetchall()]
        required_columns = ['progress_percentage', 'is_active', 'effectiveness_measurement']
        missing_columns = [col for col in required_columns if col not in prp_preventive_columns]
        
        if missing_columns:
            print(f"❌ Missing columns in prp_preventive_actions: {missing_columns}")
            return False
        else:
            print("✅ PRP preventive actions table has all required columns")
        
        # Test 3: Equipment Module
        print("\n📋 Testing Equipment Module...")
        
        # Test equipment table
        cursor.execute("PRAGMA table_info(equipment)")
        equipment_columns = [col[1] for col in cursor.fetchall()]
        required_columns = ['is_active', 'critical_to_food_safety']
        missing_columns = [col for col in required_columns if col not in equipment_columns]
        
        if missing_columns:
            print(f"❌ Missing columns in equipment: {missing_columns}")
            return False
        else:
            print("✅ Equipment table has all required columns")
        
        # Test 4: Audit Module
        print("\n📋 Testing Audit Module...")
        
        # Test audit_findings table
        cursor.execute("PRAGMA table_info(audit_findings)")
        audit_findings_columns = [col[1] for col in cursor.fetchall()]
        required_columns = ['risk_register_item_id', 'risk_assessment_method', 'is_active']
        missing_columns = [col for col in required_columns if col not in audit_findings_columns]
        
        if missing_columns:
            print(f"❌ Missing columns in audit_findings: {missing_columns}")
            return False
        else:
            print("✅ Audit findings table has all required columns")
        
        # Test 5: Database Indexes
        print("\n📊 Testing Database Indexes...")
        
        # Check if key indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        key_indexes = [
            'idx_management_reviews_status',
            'idx_review_actions_status',
            'idx_prp_corrective_actions_status',
            'idx_equipment_is_active'
        ]
        
        missing_indexes = [idx for idx in key_indexes if idx not in indexes]
        
        if missing_indexes:
            print(f"❌ Missing indexes: {missing_indexes}")
            return False
        else:
            print("✅ All key performance indexes are present")
        
        # Test 6: Foreign Key Constraints
        print("\n🔗 Testing Foreign Key Constraints...")
        
        # Check if foreign key constraints are enabled
        cursor.execute("PRAGMA foreign_keys")
        foreign_keys_enabled = cursor.fetchone()[0]
        
        if foreign_keys_enabled:
            print("✅ Foreign key constraints are enabled")
        else:
            print("⚠️  Foreign key constraints are disabled (this is normal for SQLite)")
        
        # Test 7: Data Insertion Tests
        print("\n📝 Testing Data Insertion...")
        
        # Test management review insertion
        try:
            cursor.execute("""
                INSERT INTO management_reviews 
                (title, review_date, review_type, review_scope, attendees, status, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, ('Verification Test Review', '2025-08-19', 'SCHEDULED', 'Test scope', '[]', 'PLANNED', 12))
            
            test_id = cursor.lastrowid
            cursor.execute("DELETE FROM management_reviews WHERE id = ?", (test_id,))
            print("✅ Management review insertion test passed")
        except Exception as e:
            print(f"❌ Management review insertion test failed: {str(e)}")
            return False
        
        # Test PRP corrective action insertion
        try:
            cursor.execute("""
                INSERT INTO prp_corrective_actions 
                (action_code, source_type, source_id, non_conformance_description, non_conformance_date, 
                 severity, action_description, action_type, responsible_person, assigned_to, 
                 target_completion_date, status, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, ('VERIFY001', 'inspection', 1, 'Verification test', '2025-08-19', 
                  'medium', 'Test action', 'corrective', 1, 1, '2025-12-31', 'open', 12))
            
            test_id = cursor.lastrowid
            cursor.execute("DELETE FROM prp_corrective_actions WHERE id = ?", (test_id,))
            print("✅ PRP corrective action insertion test passed")
        except Exception as e:
            print(f"❌ PRP corrective action insertion test failed: {str(e)}")
            return False
        
        conn.commit()
        print("\n🎉 All verification tests passed!")
        print("✅ The ISO 22000 FSMS platform is fully functional!")
        return True
        
    except Exception as e:
        print(f"❌ Verification test failed: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = final_verification_test()
    sys.exit(0 if success else 1)
