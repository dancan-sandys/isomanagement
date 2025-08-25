#!/usr/bin/env python3
"""
Test script for email functionality
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.email_service import EmailService
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from datetime import datetime

def test_basic_email():
    """Test basic email sending functionality"""
    print("🧪 Testing basic email functionality...")
    
    email_service = EmailService()
    
    # Test data
    test_email = "okoraok18@gmail.com"
    subject = "🧪 ISO 22000 FSMS - Email Test"
    html_content = """
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #3498db; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                <h1 style="margin-bottom: 10px;">🧪 Email Test Successful!</h1>
                <p style="font-size: 18px;">ISO 22000 FSMS Email System</p>
            </div>
            
            <div style="padding: 20px; background-color: white;">
                <h2>Email System Test</h2>
                <p>This is a test email to verify that the ISO 22000 FSMS email functionality is working correctly.</p>
                
                <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Test Details:</strong></p>
                    <p>✅ SMTP Configuration: Working</p>
                    <p>✅ Email Service: Operational</p>
                    <p>✅ Template System: Ready</p>
                    <p>✅ Notification System: Available</p>
                </div>
                
                <p><strong>Test Time:</strong> {}</p>
                <p><strong>System Status:</strong> All email functionalities are operational</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <p>This is an automated test email from the ISO 22000 FSMS.</p>
                <p>Generated on: {}</p>
            </div>
        </div>
    </body>
    </html>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    plain_content = """
🧪 Email Test Successful! - ISO 22000 FSMS Email System

Email System Test

This is a test email to verify that the ISO 22000 FSMS email functionality is working correctly.

Test Details:
✅ SMTP Configuration: Working
✅ Email Service: Operational
✅ Template System: Ready
✅ Notification System: Available

Test Time: {}
System Status: All email functionalities are operational

This is an automated test email from the ISO 22000 FSMS.
Generated on: {}
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    try:
        success = email_service.send_email(
            to_email=test_email,
            subject=subject,
            html_content=html_content,
            plain_content=plain_content
        )
        
        if success:
            print("✅ Basic email test PASSED!")
            print(f"📧 Email sent successfully to: {test_email}")
            return True
        else:
            print("❌ Basic email test FAILED!")
            print("Email service returned False")
            return False
            
    except Exception as e:
        print("❌ Basic email test FAILED!")
        print(f"Error: {str(e)}")
        return False

def test_notification_email():
    """Test notification-based email sending"""
    print("\n🧪 Testing notification email functionality...")
    
    email_service = EmailService()
    
    # Create a test notification
    notification = Notification(
        user_id=1,  # This will be ignored for the test
        title="🧪 HACCP Alert Test",
        message="This is a test HACCP alert to verify the notification email system is working correctly.",
        notification_type=NotificationType.ALERT,
        category=NotificationCategory.HACCP,
        priority=NotificationPriority.HIGH,
        notification_data={
            'product_name': 'Test Product',
            'ccp_name': 'Temperature Control',
            'batch_number': 'TEST-2024-001',
            'measured_value': '75°C',
            'limit_value': '70°C',
            'unit': '°C',
            'violation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action_url': 'https://example.com/haccp-dashboard'
        }
    )
    
    try:
        # Get user email (we'll use the test email directly)
        test_email = "okoraok18@gmail.com"
        
        # Format email content using templates
        email_content = email_service.format_email_content(notification)
        
        # Send email
        subject = f"[{notification.priority.value.upper()}] {notification.title}"
        success = email_service.send_email(
            to_email=test_email,
            subject=subject,
            html_content=email_content["html"],
            plain_content=email_content["plain"]
        )
        
        if success:
            print("✅ Notification email test PASSED!")
            print(f"📧 HACCP alert email sent successfully to: {test_email}")
            return True
        else:
            print("❌ Notification email test FAILED!")
            print("Email service returned False")
            return False
            
    except Exception as e:
        print("❌ Notification email test FAILED!")
        print(f"Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Starting ISO 22000 FSMS Email System Tests")
    print("=" * 50)
    
    # Check if email is enabled
    email_service = EmailService()
    if not email_service.enabled:
        print("❌ Email system is DISABLED!")
        print("Please enable email in your configuration:")
        print("Set EMAIL_ENABLED=true in your .env file")
        return False
    
    print(f"✅ Email system is ENABLED")
    print(f"📧 SMTP Host: {email_service.smtp_host}")
    print(f"📧 SMTP Port: {email_service.smtp_port}")
    print(f"📧 From Email: {email_service.from_email}")
    print(f"📧 From Name: {email_service.from_name}")
    
    # Run tests
    basic_test_passed = test_basic_email()
    notification_test_passed = test_notification_email()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Basic Email Test: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(f"Notification Email Test: {'✅ PASSED' if notification_test_passed else '❌ FAILED'}")
    
    if basic_test_passed and notification_test_passed:
        print("\n🎉 All email tests PASSED! Email system is working correctly.")
        return True
    else:
        print("\n⚠️ Some email tests FAILED. Please check your configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
