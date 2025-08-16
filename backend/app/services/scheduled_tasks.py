import os
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.database import get_db
from app.models.document import Document, DocumentStatus, DocumentChangeLog
from app.models.settings import ApplicationSetting
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.models.equipment import MaintenancePlan, CalibrationPlan
from app.models.audit_mgmt import Audit, AuditPlan, AuditFinding, AuditStatus, FindingStatus

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

    def enforce_document_retention_policy(self) -> dict:
        """
        Auto-obsolete/archive documents by category based on configured retention days.
        Policy keys: retention.<category>.days where category in {haccp, prp, record}
        """
        try:
            # Load retention settings
            settings_map = {s.key: s.value for s in self.db.query(ApplicationSetting).filter(ApplicationSetting.key.like('retention.%')).all()}
            now = datetime.utcnow()

            def days_for(key: str, default: int) -> int:
                try:
                    return int(settings_map.get(key, default))
                except Exception:
                    return default

            cat_days = {
                'haccp': days_for('retention.haccp.days', 1825),
                'prp': days_for('retention.prp.days', 1095),
                'record': days_for('retention.record.days', 3650),
            }

            updated = 0
            # Find candidates by category and created_at age
            candidates = self.db.query(Document).all()
            for doc in candidates:
                try:
                    created = doc.created_at or now
                    age_days = (now - created).days
                    category = (doc.category.value if doc.category else '').lower()
                    keep_days = cat_days.get(category)
                    if not keep_days:
                        continue
                    # Only apply to approved/under_review docs; draft may be excluded
                    if doc.status not in [DocumentStatus.APPROVED, DocumentStatus.UNDER_REVIEW]:
                        continue
                    if age_days >= keep_days:
                        old_status = doc.status
                        # First mark obsolete if not already
                        if doc.status != DocumentStatus.OBSOLETE:
                            doc.status = DocumentStatus.OBSOLETE
                            updated += 1
                            change_log = DocumentChangeLog(
                                document_id=doc.id,
                                change_type="status_changed",
                                change_description=f"Auto-retention: {old_status.value} -> obsolete",
                            )
                            self.db.add(change_log)
                        else:
                            # If already obsolete for > 90 days, archive
                            if doc.updated_at and (now - doc.updated_at).days >= 90:
                                doc.status = DocumentStatus.ARCHIVED
                                updated += 1
                                change_log = DocumentChangeLog(
                                    document_id=doc.id,
                                    change_type="status_changed",
                                    change_description="Auto-retention: obsolete -> archived",
                                )
                                self.db.add(change_log)
                except Exception as inner_e:
                    logger.error(f"Retention enforcement error for doc {doc.id}: {inner_e}")
                    continue

            self.db.commit()
            logger.info(f"Retention policy enforcement updated {updated} documents")
            return {"updated": updated}
        except Exception as e:
            logger.error(f"Error enforcing retention policy: {str(e)}")
            self.db.rollback()
            return {"updated": 0, "error": str(e)}
    
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
    
    def check_audit_plan_reminders(self) -> List[dict]:
        """
        Check for audits without approved plans and create reminders
        """
        try:
            now = datetime.utcnow()
            seven_days_from_now = now + timedelta(days=7)
            
            # Find audits starting within 7 days that don't have an approved plan
            audits_needing_plans = self.db.query(Audit).filter(
                and_(
                    Audit.start_date <= seven_days_from_now,
                    Audit.start_date > now,
                    Audit.status.in_([AuditStatus.PLANNED, AuditStatus.IN_PROGRESS])
                )
            ).all()
            
            reminders_created = []
            
            for audit in audits_needing_plans:
                # Check if audit has an approved plan
                approved_plan = self.db.query(AuditPlan).filter(
                    and_(
                        AuditPlan.audit_id == audit.id,
                        AuditPlan.approved_at.isnot(None)
                    )
                ).first()
                
                if not approved_plan:
                    days_until_start = (audit.start_date - now).days
                    
                    # Create notification for audit lead
                    notification = Notification(
                        user_id=audit.lead_auditor_id,
                        title="Audit Plan Required",
                        message=f"Audit '{audit.title}' (ID: {audit.id}) starts in {days_until_start} days "
                               f"but doesn't have an approved plan. Please create and submit for approval.",
                        notification_type=NotificationType.WARNING,
                        priority=NotificationPriority.HIGH if days_until_start <= 3 else NotificationPriority.MEDIUM,
                        category=NotificationCategory.AUDIT,
                        notification_data={
                            "audit_id": audit.id,
                            "start_date": audit.start_date.isoformat(),
                            "days_until_start": days_until_start
                        }
                    )
                    self.db.add(notification)
                    
                    reminders_created.append({
                        "audit_id": audit.id,
                        "title": audit.title,
                        "start_date": audit.start_date.isoformat(),
                        "days_until_start": days_until_start,
                        "notification_created": True
                    })
            
            self.db.commit()
            logger.info(f"Created {len(reminders_created)} audit plan reminders")
            return reminders_created
            
        except Exception as e:
            logger.error(f"Error checking audit plan reminders: {str(e)}")
            self.db.rollback()
            return []

    def check_findings_due_reminders(self) -> List[dict]:
        """
        Check for findings due within 7 days and overdue findings
        """
        try:
            now = datetime.utcnow()
            seven_days_from_now = now + timedelta(days=7)
            
            # Find findings due within 7 days or overdue
            findings_needing_attention = self.db.query(AuditFinding).filter(
                and_(
                    AuditFinding.target_completion_date <= seven_days_from_now,
                    AuditFinding.status.in_([FindingStatus.OPEN, FindingStatus.IN_PROGRESS])
                )
            ).all()
            
            reminders_created = []
            
            for finding in findings_needing_attention:
                days_until_due = (finding.target_completion_date - now).days
                is_overdue = days_until_due < 0
                
                # Determine priority based on severity and due date
                if is_overdue:
                    priority = NotificationPriority.HIGH
                    notification_type = NotificationType.ERROR
                    message_suffix = f"OVERDUE by {abs(days_until_due)} days"
                elif days_until_due <= 1:
                    priority = NotificationPriority.HIGH
                    notification_type = NotificationType.WARNING
                    message_suffix = f"Due tomorrow"
                elif days_until_due <= 3:
                    priority = NotificationPriority.MEDIUM
                    notification_type = NotificationType.WARNING
                    message_suffix = f"Due in {days_until_due} days"
                else:
                    priority = NotificationPriority.LOW
                    notification_type = NotificationType.INFO
                    message_suffix = f"Due in {days_until_due} days"
                
                # Create notification for finding assignee
                notification = Notification(
                    user_id=finding.responsible_person_id,
                    title=f"Finding Due: {finding.description}",
                    message=f"Finding '{finding.description}' (ID: {finding.id}) is {message_suffix}. "
                           f"Severity: {finding.severity.value}",
                    notification_type=notification_type,
                    priority=priority,
                    category=NotificationCategory.AUDIT,
                    notification_data={
                        "finding_id": finding.id,
                        "audit_id": finding.audit_id,
                        "target_completion_date": finding.target_completion_date.isoformat(),
                        "days_until_due": days_until_due,
                        "severity": finding.severity.value,
                        "is_overdue": is_overdue
                    }
                )
                self.db.add(notification)
                
                reminders_created.append({
                    "finding_id": finding.id,
                    "description": finding.description,
                    "target_completion_date": finding.target_completion_date.isoformat(),
                    "days_until_due": days_until_due,
                    "severity": finding.severity.value,
                    "is_overdue": is_overdue,
                    "notification_created": True
                })
            
            self.db.commit()
            logger.info(f"Created {len(reminders_created)} findings due reminders")
            return reminders_created
            
        except Exception as e:
            logger.error(f"Error checking findings due reminders: {str(e)}")
            self.db.rollback()
            return []

    def escalate_overdue_findings(self) -> List[dict]:
        """
        Escalate findings that are significantly overdue (more than 30 days)
        """
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)
            
            # Find findings overdue by more than 30 days
            overdue_findings = self.db.query(AuditFinding).filter(
                and_(
                    AuditFinding.target_completion_date < thirty_days_ago,
                    AuditFinding.status.in_([FindingStatus.OPEN, FindingStatus.IN_PROGRESS])
                )
            ).all()
            
            escalations_created = []
            
            for finding in overdue_findings:
                days_overdue = (now - finding.target_completion_date).days
                
                # Get audit lead for escalation
                audit = self.db.query(Audit).filter(Audit.id == finding.audit_id).first()
                if not audit or not audit.lead_auditor_id:
                    continue
                
                # Create escalation notification for audit lead
                notification = Notification(
                    user_id=audit.lead_auditor_id,
                    title="CRITICAL: Overdue Finding Escalation",
                    message=f"Finding '{finding.description}' (ID: {finding.id}) is {days_overdue} days overdue. "
                           f"Assigned to: User ID {finding.responsible_person_id}. Immediate action required.",
                    notification_type=NotificationType.ERROR,
                    priority=NotificationPriority.HIGH,
                    category=NotificationCategory.AUDIT,
                    notification_data={
                        "finding_id": finding.id,
                        "audit_id": finding.audit_id,
                        "responsible_person_id": finding.responsible_person_id,
                        "target_completion_date": finding.target_completion_date.isoformat(),
                        "days_overdue": days_overdue,
                        "severity": finding.severity.value,
                        "escalation": True
                    }
                )
                self.db.add(notification)
                
                escalations_created.append({
                    "finding_id": finding.id,
                    "description": finding.description,
                    "days_overdue": days_overdue,
                    "responsible_person_id": finding.responsible_person_id,
                    "escalation_created": True
                })
            
            self.db.commit()
            logger.info(f"Created {len(escalations_created)} overdue finding escalations")
            return escalations_created
            
        except Exception as e:
            logger.error(f"Error escalating overdue findings: {str(e)}")
            self.db.rollback()
            return []
    
    def run_all_maintenance_tasks(self) -> dict:
        """
        Run all scheduled maintenance tasks
        """
        results = {
            "archived_documents": 0,
            "review_notifications_created": 0,
            "obsolete_documents_marked": 0,
            "notifications_cleaned": 0,
            "retention_enforced": 0,
            "due_maintenance_alerts": 0,
            "due_calibration_alerts": 0,
            "audit_plan_reminders": 0,
            "findings_due_reminders": 0,
            "overdue_escalations": 0,
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

            # Enforce retention policy
            retention_result = self.enforce_document_retention_policy()
            results["retention_enforced"] = retention_result.get("updated", 0)

            # Audit-related tasks
            audit_plan_results = self.check_audit_plan_reminders()
            results["audit_plan_reminders"] = len(audit_plan_results)
            
            findings_reminder_results = self.check_findings_due_reminders()
            results["findings_due_reminders"] = len(findings_reminder_results)
            
            escalation_results = self.escalate_overdue_findings()
            results["overdue_escalations"] = len(escalation_results)

            # Alerts for equipment due dates within 7 days
            try:
                now = datetime.utcnow()
                in_seven = now + timedelta(days=7)
                due_m = self.db.query(MaintenancePlan).filter(MaintenancePlan.next_due_at != None, MaintenancePlan.next_due_at <= in_seven).all()
                for plan in due_m:
                    self.db.add(Notification(
                        user_id=1,
                        title="Maintenance Due Soon",
                        message=f"Equipment ID {plan.equipment_id} maintenance is due by {plan.next_due_at}",
                        notification_type=NotificationType.WARNING,
                        priority=NotificationPriority.MEDIUM,
                        category=NotificationCategory.MAINTENANCE
                    ))
                results["due_maintenance_alerts"] = len(due_m)
                due_c = self.db.query(CalibrationPlan).filter(CalibrationPlan.next_due_at != None, CalibrationPlan.next_due_at <= in_seven).all()
                for plan in due_c:
                    self.db.add(Notification(
                        user_id=1,
                        title="Calibration Due Soon",
                        message=f"Equipment ID {plan.equipment_id} calibration is due by {plan.next_due_at}",
                        notification_type=NotificationType.WARNING,
                        priority=NotificationPriority.MEDIUM,
                        category=NotificationCategory.MAINTENANCE
                    ))
                results["due_calibration_alerts"] = len(due_c)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                results["errors"].append(f"equipment alerts: {e}")
            
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


def run_audit_reminders():
    """
    Function to be called by external scheduler for audit-specific reminders
    """
    try:
        db = next(get_db())
        service = ScheduledTasksService(db)
        
        results = {
            "audit_plan_reminders": 0,
            "findings_due_reminders": 0,
            "overdue_escalations": 0,
            "errors": []
        }
        
        try:
            # Check audit plan reminders
            audit_plan_results = service.check_audit_plan_reminders()
            results["audit_plan_reminders"] = len(audit_plan_results)
            
            # Check findings due reminders
            findings_reminder_results = service.check_findings_due_reminders()
            results["findings_due_reminders"] = len(findings_reminder_results)
            
            # Escalate overdue findings
            escalation_results = service.escalate_overdue_findings()
            results["overdue_escalations"] = len(escalation_results)
            
        except Exception as e:
            error_msg = f"Error in audit reminders: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        logger.info(f"Audit reminders completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Failed to run audit reminders: {str(e)}")
        return {"error": str(e)}
    finally:
        db.close() 