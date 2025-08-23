# Email Setup Guide for ISO 22000 FSMS

## Overview
This guide provides comprehensive instructions for setting up email functionality in the ISO 22000 Food Safety Management System.

## 1. Email Configuration

### Environment Variables Setup
Add the following to your `.env` file:

```bash
# Email Configuration
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourcompany.com
FROM_NAME=ISO 22000 FSMS

# Email Notification Settings
EMAIL_PRIORITY_THRESHOLD=MEDIUM  # LOW, MEDIUM, HIGH, CRITICAL
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_SMS_NOTIFICATIONS=false
```

### Gmail Setup (Recommended)
1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use the app password** in `SMTP_PASSWORD`

### Alternative Email Providers
- **Outlook/Office 365**: `smtp-mail.outlook.com:587`
- **SendGrid**: `smtp.sendgrid.net:587`
- **Amazon SES**: `email-smtp.us-east-1.amazonaws.com:587`

## 2. Email Templates

### Available Templates
The system includes the following email templates:

1. **welcome_user** - New user account creation
2. **password_reset** - Password reset requests
3. **document_approval** - Document approval requests
4. **haccp_alert** - Critical HACCP violations
5. **audit_notification** - Audit scheduling and findings
6. **capa_assignment** - CAPA action assignments
7. **training_reminder** - Training schedule reminders
8. **system_maintenance** - System maintenance notifications
9. **ccp_violation** - CCP monitoring violations
10. **document_expiry** - Document expiration warnings
11. **supplier_audit** - Supplier audit notifications
12. **equipment_calibration** - Equipment calibration reminders
13. **compliance_deadline** - Regulatory compliance deadlines
14. **recall_notification** - Product recall notifications

### Customizing Templates
Templates are located in `backend/app/services/email_templates.py`. Each template supports:
- HTML and plain text versions
- Dynamic data substitution
- Responsive design
- Brand customization

## 3. Notification Categories

### System Notifications
- **User Management**: Account creation, password resets, role changes
- **System Health**: Backup status, maintenance, error alerts
- **Compliance**: Regulatory updates, deadline reminders

### HACCP Notifications
- **CCP Monitoring**: Out-of-spec readings, violations
- **HACCP Plan**: Review reminders, plan updates
- **Training**: Required training completion

### Document Management
- **Approvals**: Document approval requests
- **Status Changes**: Document approval/rejection
- **Expiry**: Document expiration warnings
- **Version Control**: New version notifications

### Audit Management
- **Scheduling**: Audit schedule notifications
- **Findings**: Audit finding notifications
- **CAPA**: Corrective action assignments
- **Reports**: Audit report distribution

### Supplier Management
- **Audit Scheduling**: Supplier audit notifications
- **Performance**: Supplier performance alerts
- **Documentation**: Supplier document updates

## 4. Email Priority Levels

### Priority Thresholds
- **LOW**: Informational messages (not emailed)
- **MEDIUM**: Standard notifications (emailed)
- **HIGH**: Important alerts (emailed)
- **CRITICAL**: Urgent notifications (emailed immediately)

### Email Frequency Settings
```python
# In email_service.py
self.email_priority_threshold = NotificationPriority.MEDIUM
```

## 5. Testing Email Configuration

### Test Email Function
```python
from app.services.email_service import EmailService

# Test email sending
email_service = EmailService()
success = email_service.send_email(
    to_email="test@example.com",
    subject="Test Email",
    html_content="<h1>Test</h1>",
    plain_content="Test"
)
print(f"Email sent: {success}")
```

### Notification Test
```python
from app.services.email_service import send_notification_email
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory

# Create test notification
notification = Notification(
    user_id=1,
    title="Test Notification",
    message="This is a test notification",
    notification_type=NotificationType.INFO,
    category=NotificationCategory.SYSTEM,
    priority=NotificationPriority.MEDIUM
)

# Send email
success = send_notification_email(notification, db_session)
```

## 6. Email Scheduling

### Automated Email Jobs
Set up cron jobs or scheduled tasks for:

1. **Daily Reports**:
   - HACCP monitoring summary
   - Document expiry warnings
   - Training completion status

2. **Weekly Reports**:
   - CAPA status updates
   - Audit schedule reminders
   - Compliance deadline alerts

3. **Monthly Reports**:
   - System performance metrics
   - User activity summary
   - Compliance status

### Example Cron Job
```bash
# Daily at 8:00 AM
0 8 * * * /usr/bin/python3 /path/to/your/app/manage.py send_daily_reports

# Weekly on Monday at 9:00 AM
0 9 * * 1 /usr/bin/python3 /path/to/your/app/manage.py send_weekly_reports
```

## 7. Email Security

### Best Practices
1. **Use App Passwords** instead of regular passwords
2. **Enable TLS/SSL** for all email connections
3. **Limit Email Access** to necessary personnel only
4. **Monitor Email Logs** for suspicious activity
5. **Regular Password Updates** for email accounts

### GDPR Compliance
- Include unsubscribe links in marketing emails
- Provide clear privacy notices
- Allow users to manage email preferences
- Maintain audit trails of email communications

## 8. Troubleshooting

### Common Issues

#### Email Not Sending
1. Check SMTP credentials
2. Verify network connectivity
3. Check firewall settings
4. Review email service logs

#### Authentication Errors
1. Verify username/password
2. Check 2FA settings
3. Generate new app password
4. Test with email client

#### Template Issues
1. Check template syntax
2. Verify data substitution
3. Test template rendering
4. Review HTML validation

### Debug Mode
Enable debug logging:
```python
import logging
logging.getLogger('app.services.email_service').setLevel(logging.DEBUG)
```

## 9. Monitoring and Analytics

### Email Metrics
Track the following metrics:
- Email delivery rates
- Open rates
- Click-through rates
- Bounce rates
- Spam complaints

### Logging
Email service logs include:
- Send attempts
- Success/failure status
- Error messages
- Performance metrics

## 10. Integration with External Services

### Email Marketing Platforms
- **Mailchimp**: For marketing campaigns
- **SendGrid**: For transactional emails
- **Mailgun**: For developer-focused email

### Notification Services
- **Slack**: Team notifications
- **Microsoft Teams**: Enterprise notifications
- **SMS**: Critical alerts via text message

## 11. Maintenance

### Regular Tasks
1. **Monitor email quotas** and limits
2. **Update email templates** as needed
3. **Review email logs** for issues
4. **Update SMTP credentials** periodically
5. **Test email functionality** regularly

### Backup and Recovery
1. **Backup email templates**
2. **Export email configuration**
3. **Document email procedures**
4. **Test recovery procedures**

## 12. Support

### Getting Help
- Check the application logs for error messages
- Review the email service documentation
- Contact system administrator for configuration issues
- Refer to email provider documentation for SMTP issues

### Documentation
- Email service API documentation
- Template customization guide
- Troubleshooting guide
- Best practices documentation
