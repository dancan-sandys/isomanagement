#!/usr/bin/env python3
"""
Comprehensive test script for notification service across all modules
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User

def setup_database():
    """Setup database connection"""
    database_url = "sqlite:///./iso22000_fsms.db"
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def test_notification_service():
    """Test all notification functionalities"""
    print("🚀 Testing ISO 22000 FSMS Notification Service")
    print("=" * 60)
    
    # Setup database session
    db = setup_database()
    notification_service = NotificationService(db)
    
    # Get test user (assuming user ID 1 exists)
    test_user = db.query(User).filter(User.id == 1).first()
    if not test_user:
        print("❌ No test user found. Please ensure user ID 1 exists in the database.")
        return False
    
    print(f"✅ Using test user: {test_user.username} (ID: {test_user.id})")
    print(f"📧 User email: {test_user.email}")
    
    test_results = []
    
    # Test 1: HACCP Violation Alert
    print("\n🧪 Test 1: HACCP Violation Alert")
    try:
        notifications = notification_service.send_haccp_violation_alert(
            user_ids=[test_user.id],
            product_name="Milk Product",
            ccp_name="Temperature Control",
            batch_number="BATCH-2024-001",
            measured_value="75°C",
            limit_value="70°C",
            unit="°C",
            action_url="https://example.com/haccp-dashboard"
        )
        print("✅ HACCP violation alert sent successfully")
        test_results.append(("HACCP Violation Alert", True))
    except Exception as e:
        print(f"❌ HACCP violation alert failed: {str(e)}")
        test_results.append(("HACCP Violation Alert", False))
    
    # Test 2: Document Approval Request
    print("\n🧪 Test 2: Document Approval Request")
    try:
        notification = notification_service.send_document_approval_request(
            approver_id=test_user.id,
            document_title="HACCP Plan 2024",
            document_type="HACCP Plan",
            submitted_by="John Doe",
            submission_date=datetime.now().strftime('%Y-%m-%d'),
            due_date=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            action_url="https://example.com/documents/approve"
        )
        print("✅ Document approval request sent successfully")
        test_results.append(("Document Approval Request", True))
    except Exception as e:
        print(f"❌ Document approval request failed: {str(e)}")
        test_results.append(("Document Approval Request", False))
    
    # Test 3: Document Expiry Warning
    print("\n🧪 Test 3: Document Expiry Warning")
    try:
        notifications = notification_service.send_document_expiry_warning(
            user_ids=[test_user.id],
            document_title="Food Safety Manual",
            expiry_date=(datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            days_until_expiry=5,
            action_url="https://example.com/documents/renew"
        )
        print("✅ Document expiry warning sent successfully")
        test_results.append(("Document Expiry Warning", True))
    except Exception as e:
        print(f"❌ Document expiry warning failed: {str(e)}")
        test_results.append(("Document Expiry Warning", False))
    
    # Test 4: Audit Schedule Notification
    print("\n🧪 Test 4: Audit Schedule Notification")
    try:
        notifications = notification_service.send_audit_schedule_notification(
            auditee_ids=[test_user.id],
            audit_title="Internal Food Safety Audit",
            audit_date=(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            auditor_name="Jane Smith",
            action_url="https://example.com/audits/schedule"
        )
        print("✅ Audit schedule notification sent successfully")
        test_results.append(("Audit Schedule Notification", True))
    except Exception as e:
        print(f"❌ Audit schedule notification failed: {str(e)}")
        test_results.append(("Audit Schedule Notification", False))
    
    # Test 5: CAPA Assignment Notification
    print("\n🧪 Test 5: CAPA Assignment Notification")
    try:
        notification = notification_service.send_capa_assignment_notification(
            assigned_user_id=test_user.id,
            capa_title="Temperature Control Improvement",
            due_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            assigned_by="Audit Team",
            action_url="https://example.com/capa/assignments"
        )
        print("✅ CAPA assignment notification sent successfully")
        test_results.append(("CAPA Assignment Notification", True))
    except Exception as e:
        print(f"❌ CAPA assignment notification failed: {str(e)}")
        test_results.append(("CAPA Assignment Notification", False))
    
    # Test 6: Training Reminder
    print("\n🧪 Test 6: Training Reminder")
    try:
        notifications = notification_service.send_training_reminder(
            user_ids=[test_user.id],
            training_title="HACCP Awareness Training",
            training_date=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            action_url="https://example.com/training/schedule"
        )
        print("✅ Training reminder sent successfully")
        test_results.append(("Training Reminder", True))
    except Exception as e:
        print(f"❌ Training reminder failed: {str(e)}")
        test_results.append(("Training Reminder", False))
    
    # Test 7: Equipment Calibration Reminder
    print("\n🧪 Test 7: Equipment Calibration Reminder")
    try:
        notifications = notification_service.send_equipment_calibration_reminder(
            user_ids=[test_user.id],
            equipment_name="Temperature Probe T-001",
            calibration_date=(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            days_until_calibration=3,
            action_url="https://example.com/equipment/calibration"
        )
        print("✅ Equipment calibration reminder sent successfully")
        test_results.append(("Equipment Calibration Reminder", True))
    except Exception as e:
        print(f"❌ Equipment calibration reminder failed: {str(e)}")
        test_results.append(("Equipment Calibration Reminder", False))
    
    # Test 8: System Maintenance Notification
    print("\n🧪 Test 8: System Maintenance Notification")
    try:
        notifications = notification_service.send_system_maintenance_notification(
            user_ids=[test_user.id],
            maintenance_type="Database Backup",
            scheduled_time=(datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
            duration="30 minutes",
            action_url="https://example.com/maintenance/schedule"
        )
        print("✅ System maintenance notification sent successfully")
        test_results.append(("System Maintenance Notification", True))
    except Exception as e:
        print(f"❌ System maintenance notification failed: {str(e)}")
        test_results.append(("System Maintenance Notification", False))
    
    # Test 9: Welcome Notification
    print("\n🧪 Test 9: Welcome Notification")
    try:
        notification = notification_service.send_welcome_notification(
            user_id=test_user.id,
            username=test_user.username,
            role_name="HACCP Team Member",
            department="Quality Assurance",
            login_url="https://example.com/login"
        )
        print("✅ Welcome notification sent successfully")
        test_results.append(("Welcome Notification", True))
    except Exception as e:
        print(f"❌ Welcome notification failed: {str(e)}")
        test_results.append(("Welcome Notification", False))
    
    # Test 10: Password Reset Notification
    print("\n🧪 Test 10: Password Reset Notification")
    try:
        notification = notification_service.send_password_reset_notification(
            user_id=test_user.id,
            reset_url="https://example.com/reset-password?token=abc123",
            expiry_time=(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')
        )
        print("✅ Password reset notification sent successfully")
        test_results.append(("Password Reset Notification", True))
    except Exception as e:
        print(f"❌ Password reset notification failed: {str(e)}")
        test_results.append(("Password Reset Notification", False))
    
    # Print test results summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<35} {status}")
        if success:
            passed_tests += 1
    
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All notification tests PASSED! Email system is fully operational.")
        print("📧 Check your email inbox for test notifications.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) FAILED. Please check the configuration.")
    
    db.close()
    return passed_tests == total_tests

def main():
    """Main function"""
    success = test_notification_service()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
