#!/usr/bin/env python3
"""
Script to add missing action_log_id column to ccp_monitoring_logs table
"""
import sqlite3
import sys

def fix_ccp_monitoring_logs_schema():
    """Add missing action_log_id column to ccp_monitoring_logs table"""
    
    try:
        # Connect to the database
        conn = sqlite3.connect("iso22000_fsms.db")
        cursor = conn.cursor()
        
        print("🔧 Fixing CCP Monitoring Logs Schema")
        print("=" * 50)
        
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(ccp_monitoring_logs)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'action_log_id' in columns:
            print("✅ action_log_id column already exists in ccp_monitoring_logs table")
            return True
        
        print("📋 Current columns in ccp_monitoring_logs:")
        for column in columns:
            print(f"   - {column}")
        
        print("\n🔨 Adding missing action_log_id column...")
        
        # Add the missing column
        cursor.execute("""
            ALTER TABLE ccp_monitoring_logs 
            ADD COLUMN action_log_id INTEGER REFERENCES action_logs(id)
        """)
        
        # Create index for the new column
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ccp_monitoring_logs_action_log_id 
            ON ccp_monitoring_logs(action_log_id)
        """)
        
        conn.commit()
        
        print("✅ Successfully added action_log_id column to ccp_monitoring_logs table")
        print("✅ Created index for action_log_id column")
        
        # Verify the column was added
        cursor.execute("PRAGMA table_info(ccp_monitoring_logs)")
        updated_columns = [column[1] for column in cursor.fetchall()]
        
        print("\n📋 Updated columns in ccp_monitoring_logs:")
        for column in updated_columns:
            print(f"   - {column}")
        
        if 'action_log_id' in updated_columns:
            print("\n✅ Schema fix completed successfully!")
            return True
        else:
            print("\n❌ Failed to add action_log_id column")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔧 CCP Monitoring Logs Schema Fix Tool")
    print("=" * 50)
    
    if fix_ccp_monitoring_logs_schema():
        print("\n🎉 The HACCP dashboard should now work correctly!")
        print("Try refreshing the HACCP module in the frontend.")
    else:
        print("\n❌ Schema fix failed. Please check the error messages above.")
        sys.exit(1)

