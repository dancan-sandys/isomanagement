import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from datetime import datetime

from app.models.notification import Notification, NotificationPriority, NotificationType, NotificationCategory
from app.models.user import User
from app.core.config import settings
from app.services.email_templates import EmailTemplates

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications
    """
    
    def __init__(self):
        self.enabled = getattr(settings, 'EMAIL_ENABLED', True)  # Default to True
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USER', '')  # Use SMTP_USER instead of SMTP_USERNAME
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@iso-system.com')
        self.from_name = getattr(settings, 'FROM_NAME', 'ISO 22000 FSMS')
        
        # Priority threshold for email notifications
        self.email_priority_threshold = NotificationPriority.MEDIUM
        
    def should_send_email(self, notification: Notification) -> bool:
        """
        Determine if an email should be sent for this notification
        """
        if not self.enabled:
            return False
            
        # Only send emails for high priority notifications
        if notification.priority.value < self.email_priority_threshold.value:
            return False
            
        # Only send for certain notification types
        email_types = [
            NotificationType.ERROR,
            NotificationType.WARNING
        ]
        
        return notification.notification_type in email_types
    
    def get_user_email(self, user_id: int, db_session) -> Optional[str]:
        """
        Get user's email address
        """
        try:
            user = db_session.query(User).filter(User.id == user_id).first()
            return user.email if user else None
        except Exception as e:
            logger.error(f"Error getting user email for user {user_id}: {str(e)}")
            return None
    
    def format_email_content(self, notification: Notification) -> Dict[str, str]:
        """
        Format notification content for email using templates
        """
        # Determine template based on notification category and type
        template_name = self._get_template_name(notification)
        
        # Prepare template data
        template_data = {
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority.value,
            'type': notification.notification_type.value,
            'category': notification.category.value,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'action_url': notification.action_url,
            'action_text': notification.action_text,
        }
        
        # Add notification data if available
        if notification.notification_data:
            template_data.update(notification.notification_data)
        
        # Get template content
        return EmailTemplates.get_template(template_name, template_data)
    
    def _get_template_name(self, notification: Notification) -> str:
        """
        Determine which template to use based on notification properties
        """
        # HACCP alerts
        if notification.category == NotificationCategory.HACCP:
            if notification.priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL]:
                return 'haccp_alert'
            return 'default'
        
        # Document approvals
        if notification.category == NotificationCategory.DOCUMENT:
            if 'approval' in notification.title.lower() or 'approve' in notification.title.lower():
                return 'document_approval'
            if 'expiry' in notification.title.lower() or 'expire' in notification.title.lower():
                return 'document_expiry'
            return 'default'
        
        # Audit notifications
        if notification.category == NotificationCategory.AUDIT:
            return 'audit_notification'
        
        # Training reminders
        if notification.category == NotificationCategory.TRAINING:
            return 'training_reminder'
        
        # Default template
        return 'default'
    
    def send_email(self, to_email: str, subject: str, html_content: str, plain_content: str) -> bool:
        """
        Send email using configured SMTP settings
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Attach both HTML and plain text versions
            text_part = MIMEText(plain_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def process_notification(self, notification: Notification, db_session) -> bool:
        """
        Process a notification and send email if appropriate
        """
        if not self.should_send_email(notification):
            return False
        
        # Get user's email
        user_email = self.get_user_email(notification.user_id, db_session)
        if not user_email:
            logger.warning(f"No email found for user {notification.user_id}")
            return False
        
        # Format email content
        email_content = self.format_email_content(notification)
        
        # Send email
        subject = f"[{notification.priority.value.upper()}] {notification.title}"
        success = self.send_email(
            to_email=user_email,
            subject=subject,
            html_content=email_content["html"],
            plain_content=email_content["plain"]
        )
        
        return success


def send_notification_email(notification: Notification, db_session) -> bool:
    """
    Convenience function to send email for a notification
    """
    email_service = EmailService()
    return email_service.process_notification(notification, db_session)


def send_bulk_notification_emails(notifications: list, db_session) -> Dict[str, int]:
    """
    Send emails for multiple notifications
    """
    email_service = EmailService()
    results = {
        "total": len(notifications),
        "sent": 0,
        "failed": 0,
        "skipped": 0
    }
    
    for notification in notifications:
        if email_service.should_send_email(notification):
            if email_service.process_notification(notification, db_session):
                results["sent"] += 1
            else:
                results["failed"] += 1
        else:
            results["skipped"] += 1
    
    logger.info(f"Bulk email results: {results}")
    return results
