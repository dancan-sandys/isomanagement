import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.models.document import Document, DocumentStatus, DocumentChangeLog
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User

logger = logging.getLogger(__name__)


class ScheduledTasksService:
    """
    Service for handling scheduled maintenance tasks
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def archive_obsolete_documents(self) -> int:
        """
        Automatically archive documents marked as obsolete
        """
        try:
            # Find documents that are obsolete and haven't been archived yet
            obsolete_documents = self.db.query(Document).filter(
                Document.status == DocumentStatus.OBSOLETE
            ).all()
            
            archived_count = 0
            for document in obsolete_documents:
                document.status = DocumentStatus.ARCHIVED
                document.updated_at = datetime.utcnow()
                
                # Create change log
                change_log = DocumentChangeLog(
                    document_id=document.id,
                    change_type="archived",
                    change_description="Document automatically archived by scheduled task",
                    new_version=document.version,
                    changed_by=1  # System user
                )
                self.db.add(change_log)
                
                archived_count += 1
            
            self.db.commit()
            logger.info(f"Archived {archived_count} obsolete documents")
            return archived_count
            
        except Exception as e:
            logger.error(f"Error archiving obsolete documents: {str(e)}")
            self.db.rollback()
            return 0
    
    def check_document_review_dates(self) -> List[dict]:
        """
        Check for documents that need review and create notifications
        """
        try:
            # Find documents with review_date in the past or within 30 days
            now = datetime.utcnow()
            thirty_days_from_now = now + timedelta(days=30)
            
            documents_needing_review = self.db.query(Document).filter(
                and_(
                    Document.review_date <= thirty_days_from_now,
                    Document.status.in_([DocumentStatus.APPROVED, DocumentStatus.UNDER_REVIEW])
                )
            ).all()
            
            notifications_created = []
            
            for document in documents_needing_review:
                days_until_review = (document.review_date - now).days
                
                # Create notification for document owner
                notification = Notification(
                    user_id=document.created_by,
                    title="Document Review Required",
                    message=f"Document '{document.title}' (ID: {document.document_number}) needs review. "
                           f"Review date: {document.review_date.strftime('%Y-%m-%d')}. "
                           f"{'OVERDUE' if days_until_review < 0 else f'Due in {days_until_review} days'}",
                    notification_type=NotificationType.WARNING,
                    priority=NotificationPriority.HIGH if days_until_review < 0 else NotificationPriority.MEDIUM,
                    category=NotificationCategory.DOCUMENT,
                    notification_data={
                        "document_id": document.id,
                        "document_number": document.document_number,
                        "review_date": document.review_date.isoformat(),
                        "days_until_review": days_until_review
                    }
                )
                self.db.add(notification)
                
                notifications_created.append({
                    "document_id": document.id,
                    "document_number": document.document_number,
                    "title": document.title,
                    "review_date": document.review_date.isoformat(),
                    "days_until_review": days_until_review,
                    "notification_created": True
                })
            
            self.db.commit()
            logger.info(f"Created {len(notifications_created)} review notifications")
            return notifications_created
            
        except Exception as e:
            logger.error(f"Error checking document review dates: {str(e)}")
            self.db.rollback()
            return []
    
    def mark_expired_documents_obsolete(self) -> int:
        """
        Mark documents as obsolete if they are significantly past their review date
        """
        try:
            # Find documents that are more than 90 days past their review date
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            
            expired_documents = self.db.query(Document).filter(
                and_(
                    Document.review_date < ninety_days_ago,
                    Document.status.in_([DocumentStatus.APPROVED, DocumentStatus.UNDER_REVIEW])
                )
            ).all()
            
            marked_obsolete_count = 0
            for document in expired_documents:
                old_status = document.status
                document.status = DocumentStatus.OBSOLETE
                document.updated_at = datetime.utcnow()
                
                # Create change log
                change_log = DocumentChangeLog(
                    document_id=document.id,
                    change_type="status_changed",
                    change_description=f"Document automatically marked as obsolete due to expired review date",
                    new_version=document.version,
                    changed_by=1  # System user
                )
                self.db.add(change_log)
                
                # Create notification for document owner
                notification = Notification(
                    user_id=document.created_by,
                    title="Document Marked as Obsolete",
                    message=f"Document '{document.title}' (ID: {document.document_number}) has been automatically "
                           f"marked as obsolete due to expired review date ({document.review_date.strftime('%Y-%m-%d')})",
                    notification_type=NotificationType.ERROR,
                    priority=NotificationPriority.HIGH,
                    category=NotificationCategory.DOCUMENT,
                    notification_data={
                        "document_id": document.id,
                        "document_number": document.document_number,
                        "old_status": old_status.value,
                        "new_status": DocumentStatus.OBSOLETE.value,
                        "review_date": document.review_date.isoformat()
                    }
                )
                self.db.add(notification)
                
                marked_obsolete_count += 1
            
            self.db.commit()
            logger.info(f"Marked {marked_obsolete_count} documents as obsolete")
            return marked_obsolete_count
            
        except Exception as e:
            logger.error(f"Error marking documents as obsolete: {str(e)}")
            self.db.rollback()
            return 0
    
    def cleanup_old_notifications(self, days_old: int = 90) -> int:
        """
        Clean up old notifications to prevent database bloat
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            # Delete old read notifications
            deleted_count = self.db.query(Notification).filter(
                and_(
                    Notification.created_at < cutoff_date,
                    Notification.is_read == True
                )
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old notifications")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old notifications: {str(e)}")
            self.db.rollback()
            return 0
    
    def run_all_maintenance_tasks(self) -> dict:
        """
        Run all scheduled maintenance tasks
        """
        results = {
            "archived_documents": 0,
            "review_notifications_created": 0,
            "obsolete_documents_marked": 0,
            "notifications_cleaned": 0,
            "errors": []
        }
        
        try:
            # Archive obsolete documents
            results["archived_documents"] = self.archive_obsolete_documents()
            
            # Check review dates
            review_results = self.check_document_review_dates()
            results["review_notifications_created"] = len(review_results)
            
            # Mark expired documents as obsolete
            results["obsolete_documents_marked"] = self.mark_expired_documents_obsolete()
            
            # Clean up old notifications
            results["notifications_cleaned"] = self.cleanup_old_notifications()
            
        except Exception as e:
            error_msg = f"Error in maintenance tasks: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results


def run_scheduled_maintenance():
    """
    Function to be called by external scheduler (e.g., cron, celery, etc.)
    """
    try:
        db = next(get_db())
        service = ScheduledTasksService(db)
        results = service.run_all_maintenance_tasks()
        
        logger.info(f"Maintenance tasks completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Failed to run scheduled maintenance: {str(e)}")
        return {"error": str(e)}
    finally:
        db.close() 