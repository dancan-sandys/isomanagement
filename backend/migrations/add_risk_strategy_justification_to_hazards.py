"""
Migration script to add risk_strategy_justification and subsequent_step fields to hazards table
"""
import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def migrate():
    """Add risk_strategy_justification and subsequent_step fields to hazards table"""
    
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'iso22000_fsms.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(hazards)")
        columns = [col[1] for col in cursor.fetchall()]
        
        changes_made = False
        
        # Add risk_strategy_justification if it doesn't exist
        if 'risk_strategy_justification' not in columns:
            print("Adding risk_strategy_justification column...")
            cursor.execute("""
                ALTER TABLE hazards 
                ADD COLUMN risk_strategy_justification TEXT
            """)
            changes_made = True
            print("✓ Added risk_strategy_justification column")
        else:
            print("✓ risk_strategy_justification column already exists")
        
        # Add subsequent_step if it doesn't exist
        if 'subsequent_step' not in columns:
            print("Adding subsequent_step column...")
            cursor.execute("""
                ALTER TABLE hazards 
                ADD COLUMN subsequent_step TEXT
            """)
            changes_made = True
            print("✓ Added subsequent_step column")
        else:
            print("✓ subsequent_step column already exists")
        
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
    print("HACCP Hazards Table Migration")
    print("Adding risk_strategy_justification and subsequent_step fields")
    print("=" * 60)
    print()
    
    success = migrate()
    
    if success:
        print("\nMigration completed successfully!")
        sys.exit(0)
    else:
        print("\nMigration failed!")
        sys.exit(1)


