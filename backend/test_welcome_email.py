#!/usr/bin/env python3
"""
Simple test to verify welcome email functionality
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.notification_service import NotificationService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def test_welcome_email():
    """Test welcome email functionality"""
    print("🚀 Testing Welcome Email Functionality")
    print("=" * 50)
    
    # Setup database connection
    database_url = "sqlite:///./iso22000_fsms.db"
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Create notification service
        notification_service = NotificationService(db)
        
        # Test welcome email
        print("📧 Sending test welcome email...")
        
        success = notification_service.send_welcome_notification(
            user_id=1,  # Assuming user ID 1 exists
            username="testuser",
            role_name="System Administrator",
            department="Quality Assurance",
            login_url="/login"
        )
        
        if success:
            print("✅ Welcome email sent successfully!")
            print("📧 Check okoraok18@gmail.com inbox for the welcome email")
        else:
            print("❌ Failed to send welcome email")
            
    except Exception as e:
        print(f"❌ Error testing welcome email: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_welcome_email()
