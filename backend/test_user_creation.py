#!/usr/bin/env python3
"""
Test script to isolate user creation issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserStatus
from app.models.rbac import Role
from app.core.security import get_password_hash

def test_user_creation():
    """Test user creation step by step"""
    print("🧪 Testing user creation...")
    
    db = SessionLocal()
    try:
        # Step 1: Check if roles exist
        roles = db.query(Role).all()
        print(f"📊 Found {len(roles)} roles")
        for role in roles:
            print(f"   - {role.name} (ID: {role.id})")
        
        if not roles:
            print("❌ No roles found!")
            return
        
        # Step 2: Try to create a minimal user
        print("\n🔧 Creating minimal user...")
        
        # Get first role
        default_role = roles[0]
        
        # Create user with minimal fields
        user = User(
            username="testminimal",
            email="testminimal@example.com",
            full_name="Test Minimal",
            hashed_password=get_password_hash("TestPass123!"),
            role_id=default_role.id,
            status=UserStatus.ACTIVE,
            is_active=True,
            is_verified=True
        )
        
        print("✅ User object created successfully")
        
        # Step 3: Try to add to database
        print("💾 Adding user to database...")
        db.add(user)
        print("✅ User added to session successfully")
        
        # Step 4: Try to commit
        print("💾 Committing to database...")
        db.commit()
        print("✅ User committed successfully!")
        
        # Step 5: Verify user was created
        created_user = db.query(User).filter(User.username == "testminimal").first()
        if created_user:
            print(f"✅ User verified in database: {created_user.username}")
        else:
            print("❌ User not found in database")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_user_creation()
