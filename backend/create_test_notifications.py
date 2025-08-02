#!/usr/bin/env python3
"""
Script to create test notifications for the ISO 22000 FSMS application.
This script populates the database with sample notifications for testing purposes.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.notification import Notification, NotificationType, NotificationCategory, NotificationPriority
from app.models.user import User

def create_test_notifications():
    """Create sample notifications for testing"""
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        if not users:
            print("No users found in the database. Please create users first.")
            return
        
        print(f"Found {len(users)} users. Creating test notifications...")
        
        # Sample notification data
        sample_notifications = [
            {
                "title": "HACCP Plan Review Due",
                "message": "Your HACCP plan for milk processing needs to be reviewed and updated within the next 7 days.",
                "notification_type": NotificationType.WARNING,
                "category": NotificationCategory.HACCP,
                "priority": NotificationPriority.HIGH,
                "action_url": "/haccp",
                "action_text": "Review HACCP Plan"
            },
            {
                "title": "PRP Checklist Overdue",
                "message": "Daily cleaning checklist for Production Line A is overdue. Please complete it immediately.",
                "notification_type": NotificationType.ERROR,
                "category": NotificationCategory.PRP,
                "priority": NotificationPriority.CRITICAL,
                "action_url": "/prp",
                "action_text": "Complete Checklist"
            },
            {
                "title": "Supplier Certificate Expiring",
                "message": "Certificate for supplier 'Dairy Farmers Co-op' expires in 30 days. Please contact them for renewal.",
                "notification_type": NotificationType.WARNING,
                "category": NotificationCategory.SUPPLIER,
                "priority": NotificationPriority.MEDIUM,
                "action_url": "/suppliers",
                "action_text": "View Supplier"
            },
            {
                "title": "Batch Traceability Alert",
                "message": "New batch B-2024-001 has been created and requires traceability links to be established.",
                "notification_type": NotificationType.INFO,
                "category": NotificationCategory.TRACEABILITY,
                "priority": NotificationPriority.MEDIUM,
                "action_url": "/traceability",
                "action_text": "Create Links"
            },
            {
                "title": "Document Approval Required",
                "message": "New SOP 'Cleaning Procedures v2.1' requires your approval before it can be published.",
                "notification_type": NotificationType.INFO,
                "category": NotificationCategory.DOCUMENT,
                "priority": NotificationPriority.MEDIUM,
                "action_url": "/documents",
                "action_text": "Review Document"
            },
            {
                "title": "Training Session Scheduled",
                "message": "Food Safety Training session is scheduled for tomorrow at 10:00 AM. Please confirm your attendance.",
                "notification_type": NotificationType.INFO,
                "category": NotificationCategory.TRAINING,
                "priority": NotificationPriority.LOW,
                "action_url": "/training",
                "action_text": "Confirm Attendance"
            },
            {
                "title": "Equipment Maintenance Due",
                "message": "Preventive maintenance for Pasteurizer Unit #3 is due in 5 days.",
                "notification_type": NotificationType.WARNING,
                "category": NotificationCategory.MAINTENANCE,
                "priority": NotificationPriority.MEDIUM,
                "action_url": "/maintenance",
                "action_text": "Schedule Maintenance"
            },
            {
                "title": "Audit Findings Available",
                "message": "Internal audit findings for Q1 2024 are now available for review and action planning.",
                "notification_type": NotificationType.INFO,
                "category": NotificationCategory.AUDIT,
                "priority": NotificationPriority.HIGH,
                "action_url": "/audit",
                "action_text": "Review Findings"
            },
            {
                "title": "System Maintenance Notice",
                "message": "Scheduled system maintenance will occur tonight from 2:00 AM to 4:00 AM. System may be temporarily unavailable.",
                "notification_type": NotificationType.INFO,
                "category": NotificationCategory.SYSTEM,
                "priority": NotificationPriority.LOW,
                "action_url": "/settings",
                "action_text": "View Details"
            },
            {
                "title": "Critical Temperature Alert",
                "message": "Temperature in Cold Storage Room 2 has exceeded the critical limit. Immediate action required.",
                "notification_type": NotificationType.ALERT,
                "category": NotificationCategory.HACCP,
                "priority": NotificationPriority.CRITICAL,
                "action_url": "/haccp",
                "action_text": "View Alert"
            }
        ]
        
        # Create notifications for each user
        notifications_created = 0
        
        for user in users:
            # Create 3-8 random notifications per user
            num_notifications = random.randint(3, 8)
            selected_notifications = random.sample(sample_notifications, num_notifications)
            
            for i, notification_data in enumerate(selected_notifications):
                # Randomize some properties
                is_read = random.choice([True, False])
                created_at = datetime.utcnow() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                # Add some expired notifications
                expires_at = None
                if random.random() < 0.1:  # 10% chance of expired notification
                    expires_at = datetime.utcnow() - timedelta(days=random.randint(1, 10))
                
                notification = Notification(
                    user_id=user.id,
                    title=notification_data["title"],
                    message=notification_data["message"],
                    notification_type=notification_data["notification_type"],
                    category=notification_data["category"],
                    priority=notification_data["priority"],
                    is_read=is_read,
                    read_at=datetime.utcnow() if is_read else None,
                    action_url=notification_data["action_url"],
                    action_text=notification_data["action_text"],
                    created_at=created_at,
                    expires_at=expires_at
                )
                
                db.add(notification)
                notifications_created += 1
        
        # Commit all notifications
        db.commit()
        
        print(f"✅ Successfully created {notifications_created} test notifications!")
        print(f"📊 Distribution:")
        print(f"   - Users: {len(users)}")
        print(f"   - Notifications per user: 3-8")
        print(f"   - Total notifications: {notifications_created}")
        
        # Show some statistics
        unread_count = db.query(Notification).filter(Notification.is_read == False).count()
        read_count = db.query(Notification).filter(Notification.is_read == True).count()
        
        print(f"   - Unread notifications: {unread_count}")
        print(f"   - Read notifications: {read_count}")
        
        # Show by category
        print(f"\n📋 By Category:")
        for category in NotificationCategory:
            count = db.query(Notification).filter(Notification.category == category).count()
            if count > 0:
                print(f"   - {category.value}: {count}")
        
        # Show by priority
        print(f"\n🚨 By Priority:")
        for priority in NotificationPriority:
            count = db.query(Notification).filter(Notification.priority == priority).count()
            if count > 0:
                print(f"   - {priority.value}: {count}")
        
    except Exception as e:
        print(f"❌ Error creating test notifications: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔔 Creating test notifications for ISO 22000 FSMS...")
    create_test_notifications()
    print("✅ Done!") 