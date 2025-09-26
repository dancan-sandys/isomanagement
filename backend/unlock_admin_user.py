#!/usr/bin/env python3
"""
Script to unlock the admin user account
"""

from sqlalchemy import create_engine, text

# Database connection
DATABASE_URL = 'sqlite:///iso22000_fsms.db'
engine = create_engine(DATABASE_URL)

def unlock_admin_user():
    """Unlock the admin user account by resetting failed login attempts and lock time"""
    
    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()
        
        try:
            # Reset failed login attempts and remove lock
            result = conn.execute(text("""
                UPDATE users 
                SET failed_login_attempts = 0, 
                    locked_until = NULL 
                WHERE username = 'admin'
            """))
            
            # Check if the update was successful
            if result.rowcount > 0:
                print("✅ Admin user account unlocked successfully!")
                print("   - Failed login attempts reset to 0")
                print("   - Account lock removed")
                
                # Verify the changes
                verify_result = conn.execute(text("""
                    SELECT username, failed_login_attempts, locked_until 
                    FROM users 
                    WHERE username = 'admin'
                """))
                
                user_data = verify_result.fetchone()
                if user_data:
                    print(f"\n📋 Admin account status:")
                    print(f"   - Username: {user_data[0]}")
                    print(f"   - Failed attempts: {user_data[1]}")
                    print(f"   - Locked until: {user_data[2]}")
                
            else:
                print("❌ No admin user found to unlock")
            
            # Commit the transaction
            trans.commit()
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Error unlocking admin user: {e}")
            raise

if __name__ == "__main__":
    unlock_admin_user()

