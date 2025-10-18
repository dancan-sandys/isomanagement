"""
Migration script to add objective and sop_reference fields to oprps table
"""
import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def migrate():
    """Add objective and sop_reference fields to oprps table"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'iso22000_fsms.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(oprps)")
        columns = [col[1] for col in cursor.fetchall()]
        
        changes_made = False
        
        # Add objective if it doesn't exist
        if 'objective' not in columns:
            print("Adding objective column...")
            cursor.execute("""
                ALTER TABLE oprps 
                ADD COLUMN objective TEXT
            """)
            changes_made = True
            print("✓ Added objective column")
        else:
            print("✓ objective column already exists")
        
        # Add sop_reference if it doesn't exist
        if 'sop_reference' not in columns:
            print("Adding sop_reference column...")
            cursor.execute("""
                ALTER TABLE oprps 
                ADD COLUMN sop_reference TEXT
            """)
            changes_made = True
            print("✓ Added sop_reference column")
        else:
            print("✓ sop_reference column already exists")
        
        if changes_made:
            conn.commit()
            print("\n✓ Migration completed successfully!")
        else:
            print("\n✓ No migration needed - all columns already exist")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("OPRP Table Migration")
    print("Adding objective and sop_reference fields")
    print("=" * 60)
    print()
    
    success = migrate()
    
    if success:
        print("\nMigration completed successfully!")
        sys.exit(0)
    else:
        print("\nMigration failed!")
        sys.exit(1)


