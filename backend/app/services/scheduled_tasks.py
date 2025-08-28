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
from app.models.prp import PRPProgram, PRPChecklist, PRPFrequency, ChecklistStatus
from app.services.nonconformance_service import NonConformanceService
from app.schemas.nonconformance import NonConformanceCreate, NonConformanceSource
from app.models.equipment import MaintenancePlan, CalibrationPlan
from app.models.audit_mgmt import Audit, AuditPlan, AuditFinding, AuditStatus, FindingStatus
from app.models.haccp import CCPMonitoringSchedule, CCP
from app.models.user import User
from app.models.food_safety_objectives import FoodSafetyObjective, ObjectiveProgress

logger = logging.getLogger(__name__)


class ScheduledTasksService:
    """
    Service for handling scheduled maintenance tasks
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_prp_daily_rollover(self) -> dict:
        """
        - For PRP programs with daily frequency:
          - Flag yesterday's (or earlier) incomplete checklists as non-conformance
          - Create today's checklist if not present (auto-reset/uncheck)
        Returns counts for actions taken.
        """
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1) - timedelta(microseconds=1)
            results = {
                "programs_processed": 0,
                "missed_checklists_flagged": 0,
                "checklists_marked_failed": 0,
                "today_checklists_created": 0,
                "notifications_created": 0,
            }

            # Fetch active daily PRP programs
            programs = self.db.query(PRPProgram).filter(
                PRPProgram.frequency == PRPFrequency.DAILY,
                PRPProgram.status == getattr(PRPProgram.status.property.columns[0].type.enum_class, 'ACTIVE')
            ).all()

            nc_service = NonConformanceService(self.db)

            for program in programs:
                results["programs_processed"] += 1

                # 1) Flag missed checklists (scheduled before today, not completed)
                missed = self.db.query(PRPChecklist).filter(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.scheduled_date < today_start,
                    PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
                ).all()

                for checklist in missed:
                    # Mark as failed
                    checklist.status = ChecklistStatus.FAILED
                    self.db.add(checklist)
                    results["checklists_marked_failed"] += 1

                    # Create non-conformance record
                    nc_payload = NonConformanceCreate(
                        title=f"Missed PRP Checklist: {checklist.name}",
                        description=(
                            f"Checklist '{checklist.name}' scheduled on {checklist.scheduled_date.strftime('%Y-%m-%d')} "
                            f"was not completed by due date {checklist.due_date.strftime('%Y-%m-%d')}. "
                            "Auto-flagged as non-conformance by scheduler."
                        ),
                        source=NonConformanceSource.PRP,
                        severity="medium",
                        impact_area="compliance",
                        category="missed_checklist",
                        target_resolution_date=today_start + timedelta(days=7)
                    )
                    try:
                        nc_service.create_non_conformance(nc_payload, reported_by=program.responsible_person or 1)
                        results["missed_checklists_flagged"] += 1
                    except Exception as _:
                        # continue processing other programs even if NC creation fails
                        logger.exception("Failed creating NC for missed PRP checklist")

                # 2) Create today's checklist if not exists
                existing_today = self.db.query(PRPChecklist).filter(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.scheduled_date >= today_start,
                    PRPChecklist.scheduled_date < today_end
                ).first()

                if not existing_today:
                    try:
                        checklist_code = f"PRP-CHK-{today_start.strftime('%Y%m%d')}-{program.id}"
                        name = f"{program.name} Daily Checklist {today_start.strftime('%Y-%m-%d')}"
                        new_chk = PRPChecklist(
                            program_id=program.id,
                            checklist_code=checklist_code,
                            name=name,
                            description=f"Auto-generated daily checklist for {program.name}",
                            status=ChecklistStatus.PENDING,
                            scheduled_date=today_start,
                            due_date=today_end,
                            assigned_to=program.responsible_person or 1,
                            created_by=program.created_by or 1
                        )
                        self.db.add(new_chk)
                        results["today_checklists_created"] += 1

                        # Optional: notify assignee
                        try:
                            self.db.add(Notification(
                                user_id=new_chk.assigned_to,
                                title="New Daily PRP Checklist",
                                message=f"'{new_chk.name}' is ready for completion today.",
                                notification_type=NotificationType.INFO,
                                priority=NotificationPriority.MEDIUM,
                                category=NotificationCategory.PRP,
                                notification_data={
                                    "program_id": program.id,
                                    "checklist_id": None,
                                    "scheduled_date": today_start.isoformat(),
                                }
                            ))
                            results["notifications_created"] += 1
                        except Exception:
                            logger.debug("Notification creation failed for PRP daily checklist", exc_info=True)
                    except Exception:
                        logger.exception("Failed creating today's PRP checklist")

            self.db.commit()
            return results
        except Exception as e:
            logger.error(f"Error in PRP daily rollover: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
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

    def check_objectives_review_reminders(self) -> List[dict]:
        """
        Check objectives with upcoming or overdue next_review_date and create notifications for owners.
        """
        try:
            now = datetime.utcnow()
            fourteen_days_from_now = now + timedelta(days=14)
            # Fetch objectives with a next_review_date due within 14 days or overdue and active
            objectives = self.db.query(FoodSafetyObjective).filter(
                FoodSafetyObjective.status == 'active',
                FoodSafetyObjective.next_review_date != None,
                FoodSafetyObjective.next_review_date <= fourteen_days_from_now
            ).all()

            created = []
            for obj in objectives:
                days_until = (obj.next_review_date - now).days if obj.next_review_date else None
                is_overdue = days_until is not None and days_until < 0
                owner_id = obj.owner_user_id or obj.responsible_person_id or obj.created_by
                if not owner_id:
                    continue
                title = "Objective Review Due" if not is_overdue else "Objective Review OVERDUE"
                msg_suffix = f"Due in {days_until} days" if days_until is not None and days_until >= 0 else f"Overdue by {abs(days_until)} days"
                notification = Notification(
                    user_id=owner_id,
                    title=title,
                    message=(
                        f"Objective '{obj.title}' (Code: {obj.objective_code}) requires review. "
                        f"Next review date: {obj.next_review_date.strftime('%Y-%m-%d')}. {msg_suffix}."
                    ),
                    notification_type=NotificationType.WARNING if not is_overdue else NotificationType.ERROR,
                    priority=NotificationPriority.HIGH if is_overdue else NotificationPriority.MEDIUM,
                    category=NotificationCategory.SYSTEM,
                    notification_data={
                        "objective_id": obj.id,
                        "objective_code": obj.objective_code,
                        "next_review_date": obj.next_review_date.isoformat(),
                        "days_until": days_until,
                        "overdue": is_overdue
                    }
                )
                self.db.add(notification)
                created.append({
                    "objective_id": obj.id,
                    "overdue": is_overdue,
                    "days_until": days_until
                })

            self.db.commit()
            logger.info(f"Created {len(created)} objective review notifications")
            return created
        except Exception as e:
            logger.error(f"Error checking objective reviews: {e}")
            self.db.rollback()
            return []

    def check_objectives_progress_activity(self) -> List[dict]:
        """
        Alert on objectives with no recent progress based on measurement_frequency.
        """
        try:
            now = datetime.utcnow()

            def max_age_days(freq: Optional[str]) -> int:
                if not freq:
                    return 60
                f = (freq or '').lower()
                if 'daily' in f:
                    return 3
                if 'weekly' in f:
                    return 14
                if 'monthly' in f:
                    return 45
                if 'quarter' in f:
                    return 120
                if 'annual' in f or 'year' in f:
                    return 400
                return 60

            alerts = []
            objectives = self.db.query(FoodSafetyObjective).filter(FoodSafetyObjective.status == 'active').all()
            for obj in objectives:
                threshold_days = max_age_days(obj.measurement_frequency)
                recent = self.db.query(ObjectiveProgress).filter(
                    ObjectiveProgress.objective_id == obj.id
                ).order_by(ObjectiveProgress.period_end.desc()).first()
                last_date = recent.period_end if recent else None
                days_since = (now - last_date).days if last_date else None
                if days_since is None or days_since > threshold_days:
                    owner_id = obj.owner_user_id or obj.responsible_person_id or obj.created_by
                    notification = Notification(
                        user_id=owner_id or 1,
                        title="No Recent Objective Progress",
                        message=(
                            f"Objective '{obj.title}' (Code: {obj.objective_code}) has no progress "
                            f"for {days_since if days_since is not None else 'N/A'} days (threshold {threshold_days})."
                        ),
                        notification_type=NotificationType.WARNING,
                        priority=NotificationPriority.MEDIUM,
                        category=NotificationCategory.SYSTEM,
                        notification_data={
                            "objective_id": obj.id,
                            "objective_code": obj.objective_code,
                            "last_progress_end": last_date.isoformat() if last_date else None,
                            "days_since": days_since,
                            "threshold_days": threshold_days
                        }
                    )
                    self.db.add(notification)
                    alerts.append({
                        "objective_id": obj.id,
                        "days_since": days_since,
                        "threshold_days": threshold_days
                    })

            self.db.commit()
            logger.info(f"Created {len(alerts)} no-progress alerts for objectives")
            return alerts
        except Exception as e:
            logger.error(f"Error checking objective progress activity: {e}")
            self.db.rollback()
            return []
    
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
            "missed_monitoring_alerts": 0,
            "errors": [],
            "objective_review_notifications": 0,
            "objective_no_progress_alerts": 0,
            "prp_daily_rollover": {"programs_processed": 0, "missed_checklists_flagged": 0, "checklists_marked_failed": 0, "today_checklists_created": 0, "notifications_created": 0}
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

            # Objectives-related tasks
            try:
                obj_review_results = self.check_objectives_review_reminders()
                results["objective_review_notifications"] = len(obj_review_results)
            except Exception as e:
                results["errors"].append(f"objective reviews: {e}")
            try:
                obj_no_progress = self.check_objectives_progress_activity()
                results["objective_no_progress_alerts"] = len(obj_no_progress)
            except Exception as e:
                results["errors"].append(f"objective no progress: {e}")

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
            
            # Missed monitoring check
            try:
                check_missed_monitoring()
                results["missed_monitoring_alerts"] = 1  # Count as 1 task executed
            except Exception as e:
                results["errors"].append(f"missed monitoring check: {e}")

            # PRP daily rollover (generate today's checklists and flag missed)
            try:
                prp_results = self.process_prp_daily_rollover()
                if isinstance(prp_results, dict):
                    results["prp_daily_rollover"] = prp_results
            except Exception as e:
                results["errors"].append(f"prp daily rollover: {e}")

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


def check_missed_monitoring():
    """Check for missed monitoring and send alerts"""
    from app.core.database import get_db
    from app.services.haccp_service import HACCPService
    from app.services.notification_service import NotificationService
    from app.models.haccp import CCPMonitoringSchedule
    from datetime import datetime, timedelta
    
    logger.info("Starting missed monitoring check...")
    
    try:
        db = next(get_db())
        haccp_service = HACCPService(db)
        notification_service = NotificationService(db)
        
        # Get all overdue monitoring schedules
        overdue_schedules = haccp_service.get_all_due_monitoring()
        overdue_count = len([s for s in overdue_schedules if s.is_overdue])
        
        if overdue_count == 0:
            logger.info("No overdue monitoring found")
            return
        
        logger.info(f"Found {overdue_count} overdue monitoring schedules")
        
        # Group by responsible users
        overdue_by_user = {}
        for schedule in overdue_schedules:
            if schedule.is_overdue:
                # Get the CCP to find responsible users
                ccp = db.query(CCP).filter(CCP.id == schedule.ccp_id).first()
                if ccp:
                    # Check monitoring responsible
                    if ccp.monitoring_responsible:
                        if ccp.monitoring_responsible not in overdue_by_user:
                            overdue_by_user[ccp.monitoring_responsible] = []
                        overdue_by_user[ccp.monitoring_responsible].append({
                            "ccp_id": schedule.ccp_id,
                            "ccp_name": schedule.ccp_name,
                            "next_due_time": schedule.next_due_time,
                            "tolerance_window_minutes": schedule.tolerance_window_minutes
                        })
        
        # Send notifications to responsible users
        for user_id, overdue_items in overdue_by_user.items():
            if len(overdue_items) == 1:
                item = overdue_items[0]
                title = f"Monitoring Overdue: {item['ccp_name']}"
                message = f"CCP monitoring is overdue. Next due time was {item['next_due_time'].strftime('%Y-%m-%d %H:%M')} (tolerance: {item['tolerance_window_minutes']} minutes)."
            else:
                title = f"Multiple Monitoring Tasks Overdue ({len(overdue_items)})"
                message = f"You have {len(overdue_items)} overdue monitoring tasks:\n"
                for item in overdue_items:
                    message += f"• {item['ccp_name']} (due: {item['next_due_time'].strftime('%Y-%m-%d %H:%M')})\n"
            
            # Create notification
            notification_data = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": "haccp_monitoring_overdue",
                "category": "food_safety",
                "priority": "high",
                "action_url": f"/haccp/monitoring/due"
            }
            
            notification_service.create_notification(notification_data)
            logger.info(f"Sent overdue notification to user {user_id}")
        
        # Also send to QA managers/verifiers if monitoring is severely overdue (>1 hour)
        severely_overdue = []
        for schedule in overdue_schedules:
            if schedule.is_overdue and schedule.next_due_time:
                overdue_minutes = (datetime.utcnow() - schedule.next_due_time).total_seconds() / 60
                if overdue_minutes > 60:  # More than 1 hour overdue
                    severely_overdue.append(schedule)
        
        if severely_overdue:
            # Find QA managers/verifiers
            qa_users = db.query(User).filter(
                User.role_id.in_([2, 3])  # Assuming role_id 2=QA Verifier, 3=QA Manager
            ).all()
            
            for user in qa_users:
                title = f"Critical: {len(severely_overdue)} Monitoring Tasks Severely Overdue"
                message = f"The following monitoring tasks are more than 1 hour overdue:\n"
                for schedule in severely_overdue:
                    overdue_minutes = int((datetime.utcnow() - schedule.next_due_time).total_seconds() / 60)
                    message += f"• {schedule.ccp_name} ({overdue_minutes} minutes overdue)\n"
                message += "\nImmediate attention required."
                
                notification_data = {
                    "user_id": user.id,
                    "title": title,
                    "message": message,
                    "type": "haccp_monitoring_critical",
                    "category": "food_safety",
                    "priority": "critical",
                    "action_url": f"/haccp/monitoring/due"
                }
                
                notification_service.create_notification(notification_data)
                logger.info(f"Sent critical overdue notification to QA user {user.id}")
        
        logger.info(f"Missed monitoring check completed. Sent {len(overdue_by_user)} user notifications and {len(severely_overdue)} critical alerts.")
        
    except Exception as e:
        logger.error(f"Error in missed monitoring check: {e}")
        import traceback
        logger.error(traceback.format_exc()) 