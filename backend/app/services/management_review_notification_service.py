"""
Management Review Notification and Scheduling Service
Handles automated notifications, reminders, and scheduling for management reviews
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.management_review import (
    ManagementReview, ReviewAction, ManagementReviewOutput, 
    ManagementReviewStatus, ActionStatus
)
from app.models.user import User
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.services.notification_service import NotificationService


class ManagementReviewNotificationService:
    """Service for managing notifications and scheduling for management reviews"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_service = NotificationService(db)
    
    # ==================== REVIEW SCHEDULING NOTIFICATIONS ====================
    
    def send_review_scheduled_notification(self, review: ManagementReview) -> List[Notification]:
        """Send notification when a review is scheduled"""
        notifications = []
        
        # Notify attendees
        if review.attendees:
            for attendee in review.attendees:
                if attendee.get('user_id'):
                    notification = self.notification_service.create_notification(
                        user_id=attendee['user_id'],
                        title="Management Review Scheduled",
                        message=f"You have been invited to attend '{review.title}' on {review.review_date.strftime('%Y-%m-%d %H:%M') if review.review_date else 'TBD'}",
                        notification_type=NotificationType.SYSTEM,
                        priority=NotificationPriority.MEDIUM,
                        metadata={
                            "review_id": review.id,
                            "review_title": review.title,
                            "review_date": review.review_date.isoformat() if review.review_date else None,
                            "action_type": "review_scheduled"
                        }
                    )
                    notifications.append(notification)
        
        # Notify chairperson
        if review.chairperson_id:
            notification = self.notification_service.create_notification(
                user_id=review.chairperson_id,
                title="Management Review - Chairperson Assignment",
                message=f"You have been assigned as chairperson for '{review.title}'",
                notification_type=NotificationType.ASSIGNMENT,
                priority=NotificationPriority.HIGH,
                metadata={
                    "review_id": review.id,
                    "review_title": review.title,
                    "action_type": "chairperson_assigned"
                }
            )
            notifications.append(notification)
        
        return notifications
    
    def send_review_reminder_notifications(self, days_before: int = 7) -> List[Notification]:
        """Send reminder notifications for upcoming reviews"""
        target_date = datetime.utcnow() + timedelta(days=days_before)
        
        upcoming_reviews = self.db.query(ManagementReview).filter(
            and_(
                ManagementReview.review_date <= target_date,
                ManagementReview.review_date >= datetime.utcnow(),
                ManagementReview.status == ManagementReviewStatus.PLANNED
            )
        ).all()
        
        notifications = []
        
        for review in upcoming_reviews:
            # Notify attendees
            if review.attendees:
                for attendee in review.attendees:
                    if attendee.get('user_id'):
                        notification = self.notification_service.create_notification(
                            user_id=attendee['user_id'],
                            title="Management Review Reminder",
                            message=f"Reminder: '{review.title}' is scheduled for {review.review_date.strftime('%Y-%m-%d %H:%M')}",
                            notification_type=NotificationType.REMINDER,
                            priority=NotificationPriority.MEDIUM,
                            metadata={
                                "review_id": review.id,
                                "review_title": review.title,
                                "review_date": review.review_date.isoformat(),
                                "action_type": "review_reminder",
                                "days_until_review": days_before
                            }
                        )
                        notifications.append(notification)
            
            # Notify chairperson
            if review.chairperson_id:
                notification = self.notification_service.create_notification(
                    user_id=review.chairperson_id,
                    title="Management Review Preparation Reminder",
                    message=f"Please prepare for '{review.title}' scheduled for {review.review_date.strftime('%Y-%m-%d %H:%M')}",
                    notification_type=NotificationType.REMINDER,
                    priority=NotificationPriority.HIGH,
                    metadata={
                        "review_id": review.id,
                        "review_title": review.title,
                        "review_date": review.review_date.isoformat(),
                        "action_type": "chairperson_preparation_reminder"
                    }
                )
                notifications.append(notification)
        
        return notifications
    
    def send_review_overdue_notifications(self) -> List[Notification]:
        """Send notifications for overdue reviews"""
        overdue_reviews = self.db.query(ManagementReview).filter(
            and_(
                ManagementReview.review_date < datetime.utcnow(),
                ManagementReview.status == ManagementReviewStatus.PLANNED
            )
        ).all()
        
        notifications = []
        
        for review in overdue_reviews:
            # Calculate days overdue
            days_overdue = (datetime.utcnow() - review.review_date).days
            
            # Notify chairperson
            if review.chairperson_id:
                notification = self.notification_service.create_notification(
                    user_id=review.chairperson_id,
                    title="Overdue Management Review",
                    message=f"'{review.title}' is {days_overdue} days overdue. Please reschedule or complete the review.",
                    notification_type=NotificationType.ALERT,
                    priority=NotificationPriority.HIGH,
                    metadata={
                        "review_id": review.id,
                        "review_title": review.title,
                        "days_overdue": days_overdue,
                        "action_type": "review_overdue"
                    }
                )
                notifications.append(notification)
            
            # Notify creator
            if review.created_by != review.chairperson_id:
                notification = self.notification_service.create_notification(
                    user_id=review.created_by,
                    title="Overdue Management Review",
                    message=f"'{review.title}' is {days_overdue} days overdue. Please take action.",
                    notification_type=NotificationType.ALERT,
                    priority=NotificationPriority.MEDIUM,
                    metadata={
                        "review_id": review.id,
                        "review_title": review.title,
                        "days_overdue": days_overdue,
                        "action_type": "review_overdue"
                    }
                )
                notifications.append(notification)
        
        return notifications
    
    # ==================== ACTION ITEM NOTIFICATIONS ====================
    
    def send_action_assigned_notification(self, action: ReviewAction) -> Optional[Notification]:
        """Send notification when an action is assigned"""
        if not action.assigned_to:
            return None
        
        review = self.db.query(ManagementReview).filter(ManagementReview.id == action.review_id).first()
        
        notification = self.notification_service.create_notification(
            user_id=action.assigned_to,
            title="Management Review Action Assigned",
            message=f"You have been assigned action '{action.title}' from review '{review.title if review else 'Unknown'}'",
            notification_type=NotificationType.ASSIGNMENT,
            priority=NotificationPriority.MEDIUM,
            metadata={
                "review_id": action.review_id,
                "action_id": action.id,
                "action_title": action.title,
                "due_date": action.due_date.isoformat() if action.due_date else None,
                "action_type": "action_assigned"
            }
        )
        
        return notification
    
    def send_action_due_reminder_notifications(self, days_before: int = 3) -> List[Notification]:
        """Send reminder notifications for actions due soon"""
        target_date = datetime.utcnow() + timedelta(days=days_before)
        
        due_actions = self.db.query(ReviewAction).filter(
            and_(
                ReviewAction.due_date <= target_date,
                ReviewAction.due_date >= datetime.utcnow(),
                ReviewAction.completed == False,
                ReviewAction.assigned_to.isnot(None)
            )
        ).all()
        
        notifications = []
        
        for action in due_actions:
            review = self.db.query(ManagementReview).filter(ManagementReview.id == action.review_id).first()
            
            notification = self.notification_service.create_notification(
                user_id=action.assigned_to,
                title="Management Review Action Due Soon",
                message=f"Action '{action.title}' is due on {action.due_date.strftime('%Y-%m-%d')}",
                notification_type=NotificationType.REMINDER,
                priority=NotificationPriority.MEDIUM,
                metadata={
                    "review_id": action.review_id,
                    "review_title": review.title if review else None,
                    "action_id": action.id,
                    "action_title": action.title,
                    "due_date": action.due_date.isoformat(),
                    "days_until_due": days_before,
                    "action_type": "action_due_reminder"
                }
            )
            notifications.append(notification)
        
        return notifications
    
    def send_action_overdue_notifications(self) -> List[Notification]:
        """Send notifications for overdue actions"""
        overdue_actions = self.db.query(ReviewAction).filter(
            and_(
                ReviewAction.due_date < datetime.utcnow(),
                ReviewAction.completed == False,
                ReviewAction.assigned_to.isnot(None)
            )
        ).all()
        
        notifications = []
        
        for action in overdue_actions:
            days_overdue = (datetime.utcnow() - action.due_date).days
            review = self.db.query(ManagementReview).filter(ManagementReview.id == action.review_id).first()
            
            # Notify assignee
            notification = self.notification_service.create_notification(
                user_id=action.assigned_to,
                title="Overdue Management Review Action",
                message=f"Action '{action.title}' is {days_overdue} days overdue. Please complete or update the action.",
                notification_type=NotificationType.ALERT,
                priority=NotificationPriority.HIGH,
                metadata={
                    "review_id": action.review_id,
                    "review_title": review.title if review else None,
                    "action_id": action.id,
                    "action_title": action.title,
                    "days_overdue": days_overdue,
                    "action_type": "action_overdue"
                }
            )
            notifications.append(notification)
            
            # Notify review chairperson if different from assignee
            if review and review.chairperson_id and review.chairperson_id != action.assigned_to:
                notification = self.notification_service.create_notification(
                    user_id=review.chairperson_id,
                    title="Overdue Action in Your Review",
                    message=f"Action '{action.title}' from '{review.title}' is {days_overdue} days overdue.",
                    notification_type=NotificationType.ALERT,
                    priority=NotificationPriority.MEDIUM,
                    metadata={
                        "review_id": action.review_id,
                        "review_title": review.title,
                        "action_id": action.id,
                        "action_title": action.title,
                        "assigned_to": action.assigned_to,
                        "days_overdue": days_overdue,
                        "action_type": "action_overdue_escalation"
                    }
                )
                notifications.append(notification)
        
        return notifications
    
    def send_action_completed_notification(self, action: ReviewAction) -> List[Notification]:
        """Send notification when an action is completed"""
        notifications = []
        review = self.db.query(ManagementReview).filter(ManagementReview.id == action.review_id).first()
        
        # Notify review chairperson
        if review and review.chairperson_id and review.chairperson_id != action.completed_by:
            notification = self.notification_service.create_notification(
                user_id=review.chairperson_id,
                title="Management Review Action Completed",
                message=f"Action '{action.title}' from '{review.title}' has been completed.",
                notification_type=NotificationType.UPDATE,
                priority=NotificationPriority.LOW,
                metadata={
                    "review_id": action.review_id,
                    "review_title": review.title,
                    "action_id": action.id,
                    "action_title": action.title,
                    "completed_by": action.completed_by,
                    "completed_at": action.completed_at.isoformat() if action.completed_at else None,
                    "action_type": "action_completed"
                }
            )
            notifications.append(notification)
        
        # Notify review creator if different from chairperson and completer
        if (review and review.created_by != review.chairperson_id and 
            review.created_by != action.completed_by):
            notification = self.notification_service.create_notification(
                user_id=review.created_by,
                title="Management Review Action Completed",
                message=f"Action '{action.title}' from '{review.title}' has been completed.",
                notification_type=NotificationType.UPDATE,
                priority=NotificationPriority.LOW,
                metadata={
                    "review_id": action.review_id,
                    "review_title": review.title,
                    "action_id": action.id,
                    "action_title": action.title,
                    "completed_by": action.completed_by,
                    "action_type": "action_completed"
                }
            )
            notifications.append(notification)
        
        return notifications
    
    # ==================== OUTPUT TRACKING NOTIFICATIONS ====================
    
    def send_output_assigned_notification(self, output: ManagementReviewOutput) -> Optional[Notification]:
        """Send notification when an output is assigned"""
        if not output.assigned_to:
            return None
        
        review = self.db.query(ManagementReview).filter(ManagementReview.id == output.review_id).first()
        
        notification = self.notification_service.create_notification(
            user_id=output.assigned_to,
            title="Management Review Output Assigned",
            message=f"You have been assigned to implement '{output.title}' from review '{review.title if review else 'Unknown'}'",
            notification_type=NotificationType.ASSIGNMENT,
            priority=NotificationPriority.MEDIUM,
            metadata={
                "review_id": output.review_id,
                "output_id": output.id,
                "output_title": output.title,
                "output_type": output.output_type.value,
                "target_completion_date": output.target_completion_date.isoformat() if output.target_completion_date else None,
                "action_type": "output_assigned"
            }
        )
        
        return notification
    
    def send_output_progress_update_notification(self, output: ManagementReviewOutput, old_progress: float) -> List[Notification]:
        """Send notification when output progress is updated"""
        notifications = []
        review = self.db.query(ManagementReview).filter(ManagementReview.id == output.review_id).first()
        
        # Notify review chairperson if different from the person updating
        if review and review.chairperson_id:
            notification = self.notification_service.create_notification(
                user_id=review.chairperson_id,
                title="Management Review Output Progress Updated",
                message=f"Progress on '{output.title}' updated from {old_progress}% to {output.progress_percentage}%",
                notification_type=NotificationType.UPDATE,
                priority=NotificationPriority.LOW,
                metadata={
                    "review_id": output.review_id,
                    "review_title": review.title,
                    "output_id": output.id,
                    "output_title": output.title,
                    "old_progress": old_progress,
                    "new_progress": output.progress_percentage,
                    "action_type": "output_progress_updated"
                }
            )
            notifications.append(notification)
        
        return notifications
    
    # ==================== COMPLIANCE AND EFFECTIVENESS NOTIFICATIONS ====================
    
    def send_compliance_check_notification(self, review: ManagementReview, compliance_score: float, missing_items: List[str]) -> List[Notification]:
        """Send notification about compliance check results"""
        notifications = []
        
        priority = NotificationPriority.HIGH if compliance_score < 80 else NotificationPriority.MEDIUM
        
        # Notify chairperson
        if review.chairperson_id:
            message = f"ISO compliance check for '{review.title}': {compliance_score:.1f}% compliant"
            if missing_items:
                message += f". Missing: {', '.join(missing_items[:3])}"
                if len(missing_items) > 3:
                    message += f" and {len(missing_items) - 3} more"
            
            notification = self.notification_service.create_notification(
                user_id=review.chairperson_id,
                title="Management Review Compliance Check",
                message=message,
                notification_type=NotificationType.SYSTEM,
                priority=priority,
                metadata={
                    "review_id": review.id,
                    "review_title": review.title,
                    "compliance_score": compliance_score,
                    "missing_items": missing_items,
                    "action_type": "compliance_check"
                }
            )
            notifications.append(notification)
        
        return notifications
    
    def send_effectiveness_score_notification(self, review: ManagementReview, effectiveness_score: float) -> List[Notification]:
        """Send notification about review effectiveness score"""
        notifications = []
        
        priority = NotificationPriority.HIGH if effectiveness_score < 6 else NotificationPriority.MEDIUM
        
        # Notify chairperson
        if review.chairperson_id:
            notification = self.notification_service.create_notification(
                user_id=review.chairperson_id,
                title="Management Review Effectiveness Score",
                message=f"'{review.title}' effectiveness score: {effectiveness_score:.1f}/10",
                notification_type=NotificationType.SYSTEM,
                priority=priority,
                metadata={
                    "review_id": review.id,
                    "review_title": review.title,
                    "effectiveness_score": effectiveness_score,
                    "action_type": "effectiveness_score"
                }
            )
            notifications.append(notification)
        
        return notifications
    
    # ==================== SCHEDULED NOTIFICATION TASKS ====================
    
    def run_daily_notification_tasks(self) -> Dict[str, int]:
        """Run daily notification tasks (to be called by scheduler)"""
        results = {
            "review_reminders_7_days": 0,
            "review_reminders_1_day": 0,
            "action_reminders": 0,
            "overdue_reviews": 0,
            "overdue_actions": 0
        }
        
        # Send review reminders (7 days and 1 day before)
        reminders_7_days = self.send_review_reminder_notifications(7)
        results["review_reminders_7_days"] = len(reminders_7_days)
        
        reminders_1_day = self.send_review_reminder_notifications(1)
        results["review_reminders_1_day"] = len(reminders_1_day)
        
        # Send action reminders (3 days before due)
        action_reminders = self.send_action_due_reminder_notifications(3)
        results["action_reminders"] = len(action_reminders)
        
        # Send overdue notifications
        overdue_reviews = self.send_review_overdue_notifications()
        results["overdue_reviews"] = len(overdue_reviews)
        
        overdue_actions = self.send_action_overdue_notifications()
        results["overdue_actions"] = len(overdue_actions)
        
        return results
    
    def run_weekly_notification_tasks(self) -> Dict[str, int]:
        """Run weekly notification tasks (to be called by scheduler)"""
        results = {
            "effectiveness_reports": 0,
            "compliance_checks": 0
        }
        
        # Send effectiveness reports for completed reviews
        completed_reviews = self.db.query(ManagementReview).filter(
            and_(
                ManagementReview.status == ManagementReviewStatus.COMPLETED,
                ManagementReview.completed_at >= datetime.utcnow() - timedelta(days=7)
            )
        ).all()
        
        for review in completed_reviews:
            if review.review_effectiveness_score:
                notifications = self.send_effectiveness_score_notification(review, review.review_effectiveness_score)
                results["effectiveness_reports"] += len(notifications)
        
        return results
    
    # ==================== UTILITY METHODS ====================
    
    def get_notification_preferences(self, user_id: int) -> Dict[str, bool]:
        """Get user notification preferences (placeholder for future implementation)"""
        # This would integrate with user preferences in the future
        return {
            "review_reminders": True,
            "action_assignments": True,
            "action_reminders": True,
            "overdue_alerts": True,
            "progress_updates": False,
            "effectiveness_reports": True
        }
    
    def should_send_notification(self, user_id: int, notification_type: str) -> bool:
        """Check if notification should be sent based on user preferences"""
        preferences = self.get_notification_preferences(user_id)
        return preferences.get(notification_type, True)