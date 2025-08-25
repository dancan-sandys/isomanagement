import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.services.email_service import EmailService
from app.services.email_templates import EmailTemplates

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Comprehensive notification service for ISO 22000 FSMS
    Handles both in-app notifications and email notifications
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
    
    def send_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType,
        category: NotificationCategory,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Dict[str, Any] = None,
        action_url: str = None,
        action_text: str = None,
        send_email: bool = True
    ) -> Notification:
        """
        Send a notification to a user with optional email
        """
        try:
            # Create notification record
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                category=category,
                priority=priority,
                notification_data=data,
                action_url=action_url,
                action_text=action_text
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            # Send email if requested and email service is enabled
            if send_email and self.email_service.enabled:
                self._send_email_notification(notification)
            
            logger.info(f"Notification sent to user {user_id}: {title}")
            return notification
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            self.db.rollback()
            raise
    
    def send_bulk_notifications(
        self,
        user_ids: List[int],
        title: str,
        message: str,
        notification_type: NotificationType,
        category: NotificationCategory,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Dict[str, Any] = None,
        action_url: str = None,
        action_text: str = None,
        send_email: bool = True
    ) -> List[Notification]:
        """
        Send notifications to multiple users
        """
        notifications = []
        for user_id in user_ids:
            try:
                notification = self.send_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    category=category,
                    priority=priority,
                    data=data,
                    action_url=action_url,
                    action_text=action_text,
                    send_email=send_email
                )
                notifications.append(notification)
            except Exception as e:
                logger.error(f"Error sending notification to user {user_id}: {str(e)}")
        
        return notifications
    
    def send_role_based_notifications(
        self,
        role_names: List[str],
        title: str,
        message: str,
        notification_type: NotificationType,
        category: NotificationCategory,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Dict[str, Any] = None,
        action_url: str = None,
        action_text: str = None,
        send_email: bool = True
    ) -> List[Notification]:
        """
        Send notifications to users with specific roles
        """
        # Get users with specified roles
        users = self.db.query(User).filter(
            User.role.has(User.role_name.in_(role_names))
        ).all()
        
        user_ids = [user.id for user in users]
        return self.send_bulk_notifications(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            priority=priority,
            data=data,
            action_url=action_url,
            action_text=action_text,
            send_email=send_email
        )
    
    def _send_email_notification(self, notification: Notification) -> bool:
        """
        Send email notification using the email service
        """
        try:
            # Get user's email
            user = self.db.query(User).filter(User.id == notification.user_id).first()
            if not user or not user.email:
                logger.warning(f"No email found for user {notification.user_id}")
                return False
            
            # Format email content using templates
            email_content = self.email_service.format_email_content(notification)
            
            # Send email
            subject = f"[{notification.priority.value.upper()}] {notification.title}"
            success = self.email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_content=email_content["html"],
                plain_content=email_content["plain"]
            )
            
            if success:
                logger.info(f"Email sent successfully to {user.email}")
            else:
                logger.error(f"Failed to send email to {user.email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            return False
    
    # HACCP Module Notifications
    def send_haccp_violation_alert(
        self,
        user_ids: List[int],
        product_name: str,
        ccp_name: str,
        batch_number: str,
        measured_value: str,
        limit_value: str,
        unit: str,
        action_url: str = None
    ) -> List[Notification]:
        """
        Send HACCP CCP violation alert
        """
        title = f"🚨 HACCP Critical Alert: {ccp_name} Violation"
        message = f"Critical control point violation detected for {product_name} (Batch: {batch_number})"
        
        data = {
            'product_name': product_name,
            'ccp_name': ccp_name,
            'batch_number': batch_number,
            'measured_value': measured_value,
            'limit_value': limit_value,
            'unit': unit,
            'violation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'action_url': action_url
        }
        
        return self.send_bulk_notifications(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=NotificationType.ALERT,
            category=NotificationCategory.HACCP,
            priority=NotificationPriority.CRITICAL,
            data=data,
            action_url=action_url,
            action_text="View Details & Take Action"
        )
    
    # Document Management Notifications
    def send_document_approval_request(
        self,
        approver_id: int,
        document_title: str,
        document_type: str,
        submitted_by: str,
        submission_date: str,
        due_date: str,
        action_url: str = None
    ) -> Notification:
        """
        Send document approval request notification
        """
        title = f"📋 Document Approval Required: {document_title}"
        message = f"You have been assigned as an approver for {document_title}"
        
        data = {
            'document_title': document_title,
            'document_type': document_type,
            'submitted_by': submitted_by,
            'submission_date': submission_date,
            'due_date': due_date,
            'action_url': action_url
        }
        
        return self.send_notification(
            user_id=approver_id,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            category=NotificationCategory.DOCUMENT,
            priority=NotificationPriority.MEDIUM,
            data=data,
            action_url=action_url,
            action_text="Review Document"
        )
    
    def send_document_expiry_warning(
        self,
        user_ids: List[int],
        document_title: str,
        expiry_date: str,
        days_until_expiry: int,
        action_url: str = None
    ) -> List[Notification]:
        """
        Send document expiry warning
        """
        priority = NotificationPriority.HIGH if days_until_expiry <= 7 else NotificationPriority.MEDIUM
        title = f"⚠️ Document Expiry Warning: {document_title}"
        message = f"Document '{document_title}' will expire in {days_until_expiry} days"
        
        data = {
            'document_title': document_title,
            'expiry_date': expiry_date,
            'days_until_expiry': days_until_expiry,
            'action_url': action_url
        }
        
        return self.send_bulk_notifications(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            category=NotificationCategory.DOCUMENT,
            priority=priority,
            data=data,
            action_url=action_url,
            action_text="Review Document"
        )
    
    # Audit Management Notifications
    def send_audit_schedule_notification(
        self,
        auditee_ids: List[int],
        audit_title: str,
        audit_date: str,
        auditor_name: str,
        action_url: str = None
    ) -> List[Notification]:
        """
        Send audit schedule notification
        """
        title = f"📅 Audit Scheduled: {audit_title}"
        message = f"An audit has been scheduled for {audit_date} by {auditor_name}"
        
        data = {
            'audit_title': audit_title,
            'audit_date': audit_date,
            'auditor_name': auditor_name,
            'action_url': action_url
        }
        
        return self.send_bulk_notifications(
            user_ids=auditee_ids,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            category=NotificationCategory.AUDIT,
            priority=NotificationPriority.MEDIUM,
            data=data,
            action_url=action_url,
            action_text="View Audit Details"
        )
    
    def send_audit_finding_notification(
        self,
        user_ids: List[int],
        audit_title: str,
        finding_count: int,
        severity: str,
        action_url: str = None
    ) -> List[Notification]:
        """
        Send audit finding notification
        """
        title = f"🔍 Audit Findings: {audit_title}"
        message = f"Audit '{audit_title}' has {finding_count} findings requiring attention"
        
        data = {
            'audit_title': audit_title,
            'finding_count': finding_count,
            'severity': severity,
            'action_url': action_url
        }
        
        priority = NotificationPriority.HIGH if severity == "Critical" else NotificationPriority.MEDIUM
        
        return self.send_bulk_notifications(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            category=NotificationCategory.AUDIT,
            priority=priority,
            data=data,
            action_url=action_url,
            action_text="Review Findings"
        )
    
    # CAPA Notifications
    def send_capa_assignment_notification(
        self,
        assigned_user_id: int,
        capa_title: str,
        due_date: str,
        assigned_by: str,
        action_url: str = None
    ) -> Notification:
        """
        Send CAPA assignment notification
        """
        title = f"📋 CAPA Assignment: {capa_title}"
        message = f"You have been assigned a CAPA action due on {due_date}"
        
        data = {
            'capa_title': capa_title,
            'due_date': due_date,
            'assigned_by': assigned_by,
            'action_url': action_url
        }
        
        return self.send_notification(
            user_id=assigned_user_id,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            category=NotificationCategory.AUDIT,  # CAPA is part of audit management
            priority=NotificationPriority.HIGH,
            data=data,
            action_url=action_url,
            action_text="View CAPA Details"
        )
    
    def send_capa_due_reminder(
        self,
        user_ids: List[int],
        capa_title: str,
        days_overdue: int,
        action_url: str = None
    ) -> List[Notification]:
        """
        Send CAPA due date reminder
        """
        title = f"⏰ CAPA Overdue: {capa_title}"
        message = f"CAPA action '{capa_title}' is {days_overdue} days overdue"
        
        data = {
            'capa_title': capa_title,
            'days_overdue': days_overdue,
            'action_url': action_url
        }
        
        return self.send_bulk_notifications(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            category=NotificationCategory.AUDIT,
            priority=NotificationPriority.HIGH,
            data=data,
            action_url=action_url,
            action_text="Complete CAPA Action"
        )
    
    # Training Notifications
    def send_training_reminder(
        self,
        user_ids: List[int],
        training_title: str,
        training_date: str,
        action_url: str = None
    ) -> List[Notification]:
        """
        Send training reminder notification
        """
        title = f"🎓 Training Reminder: {training_title}"
        message = f"Training session '{training_title}' is scheduled for {training_date}"
        
        data = {
            'training_title': training_title,
            'training_date': training_date,
            'action_url': action_url
        }
        
        return self.send_bulk_notifications(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            category=NotificationCategory.TRAINING,
            priority=NotificationPriority.MEDIUM,
            data=data,
            action_url=action_url,
            action_text="View Training Details"
        )
    
    # Equipment Notifications
    def send_equipment_calibration_reminder(
        self,
        user_ids: List[int],
        equipment_name: str,
        calibration_date: str,
        days_until_calibration: int,
        action_url: str = None
    ) -> List[Notification]:
        """
        Send equipment calibration reminder
        """
        priority = NotificationPriority.HIGH if days_until_calibration <= 7 else NotificationPriority.MEDIUM
        title = f"🔧 Equipment Calibration: {equipment_name}"
        message = f"Equipment '{equipment_name}' requires calibration in {days_until_calibration} days"
        
        data = {
            'equipment_name': equipment_name,
            'calibration_date': calibration_date,
            'days_until_calibration': days_until_calibration,
            'action_url': action_url
        }
        
        return self.send_bulk_notifications(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=NotificationType.WARNING,
            category=NotificationCategory.MAINTENANCE,
            priority=priority,
            data=data,
            action_url=action_url,
            action_text="Schedule Calibration"
        )
    
    # System Notifications
    def send_system_maintenance_notification(
        self,
        user_ids: List[int],
        maintenance_type: str,
        scheduled_time: str,
        duration: str,
        action_url: str = None
    ) -> List[Notification]:
        """
        Send system maintenance notification
        """
        title = f"🔧 System Maintenance: {maintenance_type}"
        message = f"System maintenance scheduled for {scheduled_time} (Duration: {duration})"
        
        data = {
            'maintenance_type': maintenance_type,
            'scheduled_time': scheduled_time,
            'duration': duration,
            'action_url': action_url
        }
        
        return self.send_bulk_notifications(
            user_ids=user_ids,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            category=NotificationCategory.SYSTEM,
            priority=NotificationPriority.MEDIUM,
            data=data,
            action_url=action_url,
            action_text="View Maintenance Details"
        )
    
    # User Management Notifications
    def send_welcome_notification(
        self,
        user_id: int,
        username: str,
        role_name: str,
        department: str,
        login_url: str
    ) -> Notification:
        """
        Send welcome notification to new user
        """
        title = "🎉 Welcome to ISO 22000 FSMS"
        message = f"Welcome {username}! Your account has been successfully created."
        
        data = {
            'username': username,
            'role_name': role_name,
            'department': department,
            'login_url': login_url
        }
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.SUCCESS,
            category=NotificationCategory.USER,
            priority=NotificationPriority.LOW,
            data=data,
            action_url=login_url,
            action_text="Login to System"
        )
    
    def send_password_reset_notification(
        self,
        user_id: int,
        reset_url: str,
        expiry_time: str
    ) -> Notification:
        """
        Send password reset notification
        """
        title = "🔐 Password Reset Request"
        message = f"Your password reset link will expire at {expiry_time}"
        
        data = {
            'reset_url': reset_url,
            'expiry_time': expiry_time
        }
        
        return self.send_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.INFO,
            category=NotificationCategory.USER,
            priority=NotificationPriority.MEDIUM,
            data=data,
            action_url=reset_url,
            action_text="Reset Password"
        )
