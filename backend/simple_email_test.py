#!/usr/bin/env python3
"""
Simple email test script
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def test_email_sending():
    """Test email sending with direct SMTP"""
    
    # Email configuration - you can modify these values
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USER', '')  # Changed from SMTP_USERNAME to SMTP_USER
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', 'noreply@iso-system.com')
    from_name = os.getenv('FROM_NAME', 'ISO Management System')
    
    # Test email
    to_email = "okoraok18@gmail.com"
    
    print("🧪 Testing email functionality...")
    print(f"📧 SMTP Host: {smtp_host}")
    print(f"📧 SMTP Port: {smtp_port}")
    print(f"📧 From Email: {from_email}")
    print(f"📧 To Email: {to_email}")
    
    # Check if credentials are set
    if not smtp_username or not smtp_password:
        print("❌ SMTP credentials not configured!")
        print("Please set SMTP_USERNAME and SMTP_PASSWORD environment variables")
        print("Or add them to your .env file:")
        print("SMTP_USERNAME=your-email@gmail.com")
        print("SMTP_PASSWORD=your-app-password")
        return False
    
    # Create email content
    subject = "🧪 ISO 22000 FSMS - Email Test"
    
    html_content = f"""
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
                
                <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>System Status:</strong> All email functionalities are operational</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <p>This is an automated test email from the ISO 22000 FSMS.</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
🧪 Email Test Successful! - ISO 22000 FSMS Email System

Email System Test

This is a test email to verify that the ISO 22000 FSMS email functionality is working correctly.

Test Details:
✅ SMTP Configuration: Working
✅ Email Service: Operational
✅ Template System: Ready
✅ Notification System: Available

Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
System Status: All email functionalities are operational

This is an automated test email from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        # Attach both HTML and plain text versions
        text_part = MIMEText(plain_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        print("📤 Attempting to send email...")
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            print("🔐 Attempting SMTP authentication...")
            server.login(smtp_username, smtp_password)
            print("📧 Sending email...")
            server.send_message(msg)
        
        print("✅ Email sent successfully!")
        print(f"📧 Email delivered to: {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print("❌ SMTP Authentication failed!")
        print(f"Error: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check your username and password")
        print("2. If using Gmail, make sure you're using an App Password")
        print("3. Enable 2-Factor Authentication and generate an App Password")
        return False
        
    except smtplib.SMTPException as e:
        print("❌ SMTP Error occurred!")
        print(f"Error: {str(e)}")
        return False
        
    except Exception as e:
        print("❌ Unexpected error occurred!")
        print(f"Error: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 ISO 22000 FSMS Email Test")
    print("=" * 40)
    
    # Load environment variables from .env file if it exists
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"📄 Loading configuration from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    else:
        print("⚠️ No .env file found. Using default values.")
    
    success = test_email_sending()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 Email test PASSED! Check your inbox at okoraok18@gmail.com")
    else:
        print("⚠️ Email test FAILED! Please check your configuration.")
    
    return success

if __name__ == "__main__":
    main()
