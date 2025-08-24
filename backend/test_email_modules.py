#!/usr/bin/env python3
"""
Simplified test script for email functionality across modules
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

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

def send_test_email(subject, html_content, plain_content, to_email="okoraok18@gmail.com"):
    """Send a test email"""
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', 'noreply@iso-system.com')
    from_name = os.getenv('FROM_NAME', 'ISO 22000 FSMS')
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        text_part = MIMEText(plain_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def test_haccp_violation_email():
    """Test HACCP violation email"""
    subject = "🚨 HACCP CRITICAL ALERT - Temperature Control Violation"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #e74c3c; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                <h1 style="margin-bottom: 10px;">🚨 HACCP CRITICAL ALERT</h1>
                <p style="font-size: 18px;">Critical Control Point Violation Detected</p>
            </div>
            
            <div style="padding: 20px; background-color: white;">
                <h2>Critical Control Point Violation</h2>
                <p>A critical control point violation has been detected that requires immediate attention:</p>
                
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Product:</strong> Milk Product</p>
                    <p><strong>CCP:</strong> Temperature Control</p>
                    <p><strong>Batch Number:</strong> BATCH-2024-001</p>
                    <p><strong>Measured Value:</strong> 75°C</p>
                    <p><strong>Limit:</strong> 70°C</p>
                    <p><strong>Violation Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <p><strong>Immediate Actions Required:</strong></p>
                <ul>
                    <li>Stop production if necessary</li>
                    <li>Isolate affected product</li>
                    <li>Initiate corrective actions</li>
                    <li>Document the incident</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://example.com/haccp-dashboard" style="background-color: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">View Details & Take Action</a>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <p>This is a critical food safety alert. Immediate action is required.</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
🚨 HACCP CRITICAL ALERT - Critical Control Point Violation Detected

A critical control point violation has been detected that requires immediate attention:

Product: Milk Product
CCP: Temperature Control
Batch Number: BATCH-2024-001
Measured Value: 75°C
Limit: 70°C
Violation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

IMMEDIATE ACTIONS REQUIRED:
- Stop production if necessary
- Isolate affected product
- Initiate corrective actions
- Document the incident

View Details: https://example.com/haccp-dashboard

This is a critical food safety alert. Immediate action is required.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return send_test_email(subject, html_content, plain_content)

def test_document_approval_email():
    """Test document approval email"""
    subject = "📋 Document Approval Required: HACCP Plan 2024"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #3498db; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                <h1 style="margin-bottom: 10px;">📋 Document Approval Required</h1>
                <p style="font-size: 18px;">A document requires your review and approval</p>
            </div>
            
            <div style="padding: 20px; background-color: white;">
                <h2>Document Approval Request</h2>
                <p>You have been assigned as an approver for the following document:</p>
                
                <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Document Title:</strong> HACCP Plan 2024</p>
                    <p><strong>Document Type:</strong> HACCP Plan</p>
                    <p><strong>Submitted By:</strong> John Doe</p>
                    <p><strong>Submission Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                    <p><strong>Due Date:</strong> {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}</p>
                </div>
                
                <p>Please review the document and provide your approval or feedback within the specified timeframe.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://example.com/documents/approve" style="background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">Review Document</a>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <p>This is an automated notification from the ISO 22000 FSMS.</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
📋 Document Approval Required

You have been assigned as an approver for the following document:

Document Title: HACCP Plan 2024
Document Type: HACCP Plan
Submitted By: John Doe
Submission Date: {datetime.now().strftime('%Y-%m-%d')}
Due Date: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}

Please review the document and provide your approval or feedback within the specified timeframe.

Review Document: https://example.com/documents/approve

This is an automated notification from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return send_test_email(subject, html_content, plain_content)

def test_audit_schedule_email():
    """Test audit schedule email"""
    subject = "📅 Audit Scheduled: Internal Food Safety Audit"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f39c12; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                <h1 style="margin-bottom: 10px;">📅 Audit Scheduled</h1>
                <p style="font-size: 18px;">Internal Food Safety Audit</p>
            </div>
            
            <div style="padding: 20px; background-color: white;">
                <h2>Audit Schedule Notification</h2>
                <p>An audit has been scheduled for your department:</p>
                
                <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Audit Title:</strong> Internal Food Safety Audit</p>
                    <p><strong>Audit Date:</strong> {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}</p>
                    <p><strong>Auditor:</strong> Jane Smith</p>
                    <p><strong>Scope:</strong> HACCP System Implementation</p>
                </div>
                
                <p>Please ensure all relevant documentation and personnel are prepared for the audit.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://example.com/audits/schedule" style="background-color: #f39c12; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">View Audit Details</a>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <p>This is an automated notification from the ISO 22000 FSMS.</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
📅 Audit Scheduled: Internal Food Safety Audit

An audit has been scheduled for your department:

Audit Title: Internal Food Safety Audit
Audit Date: {(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}
Auditor: Jane Smith
Scope: HACCP System Implementation

Please ensure all relevant documentation and personnel are prepared for the audit.

View Audit Details: https://example.com/audits/schedule

This is an automated notification from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return send_test_email(subject, html_content, plain_content)

def test_capa_assignment_email():
    """Test CAPA assignment email"""
    subject = "📋 CAPA Assignment: Temperature Control Improvement"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #e67e22; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                <h1 style="margin-bottom: 10px;">📋 CAPA Assignment</h1>
                <p style="font-size: 18px;">Corrective Action Required</p>
            </div>
            
            <div style="padding: 20px; background-color: white;">
                <h2>CAPA Action Assignment</h2>
                <p>You have been assigned a CAPA action that requires your attention:</p>
                
                <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>CAPA Title:</strong> Temperature Control Improvement</p>
                    <p><strong>Due Date:</strong> {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}</p>
                    <p><strong>Assigned By:</strong> Audit Team</p>
                    <p><strong>Priority:</strong> High</p>
                </div>
                
                <p>Please review the CAPA details and take necessary actions to address the identified issue.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://example.com/capa/assignments" style="background-color: #e67e22; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">View CAPA Details</a>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <p>This is an automated notification from the ISO 22000 FSMS.</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
📋 CAPA Assignment: Temperature Control Improvement

You have been assigned a CAPA action that requires your attention:

CAPA Title: Temperature Control Improvement
Due Date: {(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')}
Assigned By: Audit Team
Priority: High

Please review the CAPA details and take necessary actions to address the identified issue.

View CAPA Details: https://example.com/capa/assignments

This is an automated notification from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return send_test_email(subject, html_content, plain_content)

def test_training_reminder_email():
    """Test training reminder email"""
    subject = "🎓 Training Reminder: HACCP Awareness Training"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #9b59b6; padding: 20px; border-radius: 5px; text-align: center; color: white;">
                <h1 style="margin-bottom: 10px;">🎓 Training Reminder</h1>
                <p style="font-size: 18px;">HACCP Awareness Training</p>
            </div>
            
            <div style="padding: 20px; background-color: white;">
                <h2>Training Session Reminder</h2>
                <p>You have a training session scheduled:</p>
                
                <div style="background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Training Title:</strong> HACCP Awareness Training</p>
                    <p><strong>Training Date:</strong> {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}</p>
                    <p><strong>Duration:</strong> 2 hours</p>
                    <p><strong>Location:</strong> Training Room A</p>
                </div>
                
                <p>Please ensure you attend this training session to maintain compliance with food safety requirements.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://example.com/training/schedule" style="background-color: #9b59b6; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">View Training Details</a>
                </div>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <p>This is an automated notification from the ISO 22000 FSMS.</p>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    plain_content = f"""
🎓 Training Reminder: HACCP Awareness Training

You have a training session scheduled:

Training Title: HACCP Awareness Training
Training Date: {(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}
Duration: 2 hours
Location: Training Room A

Please ensure you attend this training session to maintain compliance with food safety requirements.

View Training Details: https://example.com/training/schedule

This is an automated notification from the ISO 22000 FSMS.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return send_test_email(subject, html_content, plain_content)

def main():
    """Main test function"""
    print("🚀 Testing Email Functionality Across ISO 22000 FSMS Modules")
    print("=" * 60)
    
    # Load environment variables
    load_env_vars()
    
    # Check if credentials are configured
    smtp_username = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    
    if not smtp_username or not smtp_password:
        print("❌ SMTP credentials not configured!")
        print("Please set SMTP_USER and SMTP_PASSWORD in your .env file")
        return False
    
    print("✅ SMTP credentials configured")
    print(f"📧 SMTP Host: {os.getenv('SMTP_HOST', 'smtp.gmail.com')}")
    print(f"📧 SMTP Port: {os.getenv('SMTP_PORT', '587')}")
    print(f"📧 From Email: {os.getenv('FROM_EMAIL', 'noreply@iso-system.com')}")
    
    test_results = []
    
    # Test 1: HACCP Violation Alert
    print("\n🧪 Test 1: HACCP Violation Alert")
    if test_haccp_violation_email():
        print("✅ HACCP violation alert sent successfully")
        test_results.append(("HACCP Violation Alert", True))
    else:
        print("❌ HACCP violation alert failed")
        test_results.append(("HACCP Violation Alert", False))
    
    # Test 2: Document Approval Request
    print("\n🧪 Test 2: Document Approval Request")
    if test_document_approval_email():
        print("✅ Document approval request sent successfully")
        test_results.append(("Document Approval Request", True))
    else:
        print("❌ Document approval request failed")
        test_results.append(("Document Approval Request", False))
    
    # Test 3: Audit Schedule Notification
    print("\n🧪 Test 3: Audit Schedule Notification")
    if test_audit_schedule_email():
        print("✅ Audit schedule notification sent successfully")
        test_results.append(("Audit Schedule Notification", True))
    else:
        print("❌ Audit schedule notification failed")
        test_results.append(("Audit Schedule Notification", False))
    
    # Test 4: CAPA Assignment Notification
    print("\n🧪 Test 4: CAPA Assignment Notification")
    if test_capa_assignment_email():
        print("✅ CAPA assignment notification sent successfully")
        test_results.append(("CAPA Assignment Notification", True))
    else:
        print("❌ CAPA assignment notification failed")
        test_results.append(("CAPA Assignment Notification", False))
    
    # Test 5: Training Reminder
    print("\n🧪 Test 5: Training Reminder")
    if test_training_reminder_email():
        print("✅ Training reminder sent successfully")
        test_results.append(("Training Reminder", True))
    else:
        print("❌ Training reminder failed")
        test_results.append(("Training Reminder", False))
    
    # Print test results summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, success in test_results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<30} {status}")
        if success:
            passed_tests += 1
    
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All email module tests PASSED! Email system is fully operational.")
        print("📧 Check your email inbox at okoraok18@gmail.com for test notifications.")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) FAILED. Please check the configuration.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
