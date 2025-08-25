#!/usr/bin/env python3
"""
Simple test to verify welcome email functionality without full app imports
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_env_vars():
    """Load environment variables from .env file"""
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

def send_welcome_email():
    """Send a test welcome email"""
    print("🚀 Testing Welcome Email Functionality")
    print("=" * 50)
    
    # Load environment variables
    load_env_vars()
    
    # Get SMTP settings
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', 'noreply@iso-system.com')
    from_name = os.getenv('FROM_NAME', 'ISO 22000 FSMS')
    
    if not smtp_username or not smtp_password:
        print("❌ SMTP credentials not configured!")
        return False
    
    # Create welcome email content
    subject = "🎉 Welcome to ISO 22000 FSMS"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #27ae60; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                <h1 style="margin-bottom: 10px;">🎉 Welcome to ISO 22000 FSMS</h1>
                <p style="font-size: 18px;">Your account has been successfully created</p>
            </div>
            
            <div style="padding: 20px; background-color: white;">
                <h2>Welcome to the Food Safety Management System</h2>
                <p>Hello <strong>testuser</strong>!</p>
                <p>Your account has been successfully created in the ISO 22000 Food Safety Management System.</p>
                
                <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Account Details:</strong></p>
                    <p><strong>Username:</strong> testuser</p>
                    <p><strong>Role:</strong> System Administrator</p>
                    <p><strong>Department:</strong> Quality Assurance</p>
                    <p><strong>Account Created:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <p>You can now access the system using your credentials. Please ensure you follow all food safety protocols and maintain compliance with ISO 22000 standards.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="/login" style="background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Login to System</a>
                </div>
                
                <p><strong>Important Information:</strong></p>
                <ul>
                    <li>Keep your login credentials secure</li>
                    <li>Complete your profile information</li>
                    <li>Review your assigned responsibilities</li>
                    <li>Attend required training sessions</li>
                </ul>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <p>This is an automated welcome message from the ISO 22000 FSMS.</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
🎉 Welcome to ISO 22000 FSMS

Hello testuser!

Your account has been successfully created in the ISO 22000 Food Safety Management System.

Account Details:
- Username: testuser
- Role: System Administrator
- Department: Quality Assurance
- Account Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

You can now access the system using your credentials. Please ensure you follow all food safety protocols and maintain compliance with ISO 22000 standards.

Login to System: /login

Important Information:
- Keep your login credentials secure
- Complete your profile information
- Review your assigned responsibilities
- Attend required training sessions

This is an automated welcome message from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = "okoraok18@gmail.com"
        
        text_part = MIMEText(plain_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print("✅ Welcome email sent successfully!")
        print("📧 Check okoraok18@gmail.com inbox for the welcome email")
        return True
        
    except Exception as e:
        print(f"❌ Error sending welcome email: {str(e)}")
        return False

if __name__ == "__main__":
    success = send_welcome_email()
    exit(0 if success else 1)
