import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import uuid
import base64

from app.models.prp import (
    PRPProgram, PRPChecklist, PRPChecklistItem, PRPTemplate, PRPSchedule,
    PRPCategory, PRPFrequency, PRPStatus, ChecklistStatus
)
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.schemas.prp import (
    PRPProgramCreate, PRPProgramUpdate, ChecklistCreate, ChecklistUpdate,
    ChecklistItemCreate, ChecklistCompletion, NonConformanceCreate,
    ReminderCreate, ScheduleCreate, ResponseType
)

logger = logging.getLogger(__name__)


class PRPService:
    """
    Service for handling PRP business logic
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = "uploads/prp"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def create_prp_program(self, program_data: PRPProgramCreate, created_by: int) -> PRPProgram:
        """Create a new PRP program"""
        
        # Check if program code already exists
        existing_program = self.db.query(PRPProgram).filter(
            PRPProgram.program_code == program_data.program_code
        ).first()
        
        if existing_program:
            raise ValueError("Program code already exists")
        
        # Calculate next due date based on frequency
        next_due_date = None
        if program_data.frequency:
            next_due_date = datetime.utcnow()
            
            if program_data.frequency == PRPFrequency.DAILY:
                next_due_date += timedelta(days=1)
            elif program_data.frequency == PRPFrequency.WEEKLY:
                next_due_date += timedelta(weeks=1)
            elif program_data.frequency == PRPFrequency.MONTHLY:
                next_due_date += timedelta(days=30)
            elif program_data.frequency == PRPFrequency.QUARTERLY:
                next_due_date += timedelta(days=90)
            elif program_data.frequency == PRPFrequency.SEMI_ANNUALLY:
                next_due_date += timedelta(days=180)
            elif program_data.frequency == PRPFrequency.ANNUALLY:
                next_due_date += timedelta(days=365)
        
        program = PRPProgram(
            program_code=program_data.program_code,
            name=program_data.name,
            description=program_data.description,
            category=program_data.category,
            status=PRPStatus.ACTIVE,
            objective=program_data.objective,
            scope=program_data.scope,
            responsible_department=program_data.responsible_department,
            responsible_person=program_data.responsible_person,
            frequency=program_data.frequency,
            frequency_details=program_data.frequency_details,
            next_due_date=next_due_date,
            sop_reference=program_data.sop_reference,
            forms_required=program_data.forms_required,
            created_by=created_by
        )
        
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        
        return program
    
    def create_checklist(self, program_id: int, checklist_data: ChecklistCreate, created_by: int) -> PRPChecklist:
        """Create a new checklist"""
        
        # Verify program exists
        program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise ValueError("PRP program not found")
        
        # Check if checklist code already exists
        existing_checklist = self.db.query(PRPChecklist).filter(
            PRPChecklist.checklist_code == checklist_data.checklist_code
        ).first()
        
        if existing_checklist:
            raise ValueError("Checklist code already exists")
        
        checklist = PRPChecklist(
            program_id=program_id,
            checklist_code=checklist_data.checklist_code,
            name=checklist_data.name,
            description=checklist_data.description,
            status=ChecklistStatus.PENDING,
            scheduled_date=checklist_data.scheduled_date,
            due_date=checklist_data.due_date,
            assigned_to=checklist_data.assigned_to,
            created_by=created_by
        )
        
        self.db.add(checklist)
        self.db.commit()
        self.db.refresh(checklist)
        
        # Create reminder for the checklist
        self._create_checklist_reminder(checklist)
        
        return checklist
    
    def _create_checklist_reminder(self, checklist: PRPChecklist):
        """Create reminder for a checklist"""
        
        try:
            # Create reminder notification
            reminder_date = checklist.due_date - timedelta(days=1)
            
            notification = Notification(
                user_id=checklist.assigned_to,
                title=f"PRP Checklist Reminder: {checklist.name}",
                message=f"Checklist '{checklist.name}' is due tomorrow ({checklist.due_date.strftime('%Y-%m-%d')}). "
                       f"Please complete the checklist before the due date.",
                notification_type=NotificationType.WARNING,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.PRP,
                notification_data={
                    "checklist_id": checklist.id,
                    "checklist_code": checklist.checklist_code,
                    "due_date": checklist.due_date.isoformat(),
                    "reminder_type": "due_soon"
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.info(f"Reminder created for checklist {checklist.checklist_code}")
            
        except Exception as e:
            logger.error(f"Failed to create reminder for checklist {checklist.id}: {str(e)}")
    
    def complete_checklist(self, checklist_id: int, completion_data: ChecklistCompletion, completed_by: int) -> Tuple[PRPChecklist, bool]:
        """Complete a checklist with signature and timestamp logging"""
        
        checklist = self.db.query(PRPChecklist).filter(PRPChecklist.id == checklist_id).first()
        if not checklist:
            raise ValueError("Checklist not found")
        
        # Update checklist items
        total_items = 0
        passed_items = 0
        failed_items = 0
        not_applicable_items = 0
        
        for item_completion in completion_data.items:
            item = self.db.query(PRPChecklistItem).filter(PRPChecklistItem.id == item_completion.item_id).first()
            if item:
                item.response = item_completion.response
                item.response_value = item_completion.response_value
                item.is_compliant = item_completion.is_compliant
                item.comments = item_completion.comments
                item.evidence_files = item_completion.evidence_files
                item.updated_at = datetime.utcnow()
                
                total_items += 1
                if item_completion.is_compliant:
                    passed_items += 1
                else:
                    failed_items += 1
                
                # Check if item is not applicable
                if item_completion.response.lower() in ['n/a', 'not applicable', 'na']:
                    not_applicable_items += 1
                    passed_items -= 1  # Adjust counts
        
        # Calculate compliance percentage
        compliance_percentage = 0.0
        if total_items > 0:
            compliance_percentage = (passed_items / (total_items - not_applicable_items)) * 100 if (total_items - not_applicable_items) > 0 else 100.0
        
        # Update checklist
        checklist.status = ChecklistStatus.COMPLETED
        checklist.completed_date = datetime.utcnow()
        checklist.total_items = total_items
        checklist.passed_items = passed_items
        checklist.failed_items = failed_items
        checklist.not_applicable_items = not_applicable_items
        checklist.compliance_percentage = compliance_percentage
        checklist.general_comments = completion_data.general_comments
        checklist.corrective_actions_required = completion_data.corrective_actions_required
        checklist.corrective_actions = completion_data.corrective_actions
        checklist.updated_at = datetime.utcnow()
        
        # Store signature if provided
        signature_created = False
        if completion_data.signature:
            signature_created = self._store_signature(checklist_id, completion_data.signature, completed_by)
        
        # Check for non-conformance
        non_conformance_created = False
        if failed_items > 0 or completion_data.corrective_actions_required:
            non_conformance_created = self._create_non_conformance(checklist, completion_data)
        
        self.db.commit()
        
        return checklist, non_conformance_created
    
    def _store_signature(self, checklist_id: int, signature_data: str, signed_by: int) -> bool:
        """Store signature data for a checklist"""
        
        try:
            # Decode base64 signature
            signature_bytes = base64.b64decode(signature_data)
            
            # Generate unique filename
            filename = f"signature_{checklist_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.png"
            file_path = os.path.join(self.upload_dir, filename)
            
            # Save signature file
            with open(file_path, 'wb') as f:
                f.write(signature_bytes)
            
            # Store signature metadata in database (you might want to create a Signature model)
            # For now, we'll store it in the checklist evidence_files field
            checklist = self.db.query(PRPChecklist).filter(PRPChecklist.id == checklist_id).first()
            if checklist:
                evidence_files = []
                if checklist.evidence_files:
                    try:
                        evidence_files = json.loads(checklist.evidence_files)
                    except:
                        evidence_files = []
                
                evidence_files.append({
                    "type": "signature",
                    "filename": filename,
                    "file_path": file_path,
                    "signed_by": signed_by,
                    "signed_at": datetime.utcnow().isoformat()
                })
                
                checklist.evidence_files = json.dumps(evidence_files)
            
            logger.info(f"Signature stored for checklist {checklist_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store signature for checklist {checklist_id}: {str(e)}")
            return False
    
    def _create_non_conformance(self, checklist: PRPChecklist, completion_data: ChecklistCompletion) -> bool:
        """Create non-conformance record for failed checklist"""
        
        try:
            # Determine severity based on failure rate
            failure_rate = checklist.failed_items / checklist.total_items if checklist.total_items > 0 else 0
            
            if failure_rate >= 0.5:
                severity = "critical"
            elif failure_rate >= 0.3:
                severity = "high"
            elif failure_rate >= 0.1:
                severity = "medium"
            else:
                severity = "low"
            
            # Persist a Non-Conformance via NonConformanceService
            try:
                from app.schemas.nonconformance import NonConformanceCreate as NCCreate, NonConformanceSource
                from app.services.nonconformance_service import NonConformanceService
            except Exception:
                NonConformanceService = None  # type: ignore
            if NonConformanceService:
                nc_title = f"PRP Checklist Failure: {checklist.name}"
                nc_description = (
                    f"Checklist '{checklist.name}' failed with {checklist.failed_items} of {checklist.total_items} items. "
                    f"Compliance: {checklist.compliance_percentage:.1f}%"
                )
                nc_data = NCCreate(
                    title=nc_title,
                    description=nc_description,
                    source=NonConformanceSource.PRP,
                    batch_reference=None,
                    product_reference=None,
                    process_reference=f"PRPProgram:{checklist.program_id}/Checklist:{checklist.id}",
                    location=None,
                    severity=severity,
                    impact_area="quality",
                    category="PRP_Checklist",
                    target_resolution_date=datetime.utcnow() + timedelta(days=7),
                )
                nc_service = NonConformanceService(self.db)
                # Use checklist.creator as reporter if available; fallback to assigned_to
                reported_by = checklist.created_by or (checklist.assigned_to or 1)
                _nc = nc_service.create_non_conformance(nc_data, reported_by)
            
            # Create notification for non-conformance
            notification = Notification(
                user_id=checklist.assigned_to,
                title=f"PRP Non-Conformance Alert: {checklist.name}",
                message=f"Checklist '{checklist.name}' has failed with {checklist.failed_items} failed items. "
                       f"Compliance rate: {checklist.compliance_percentage:.1f}%. "
                       f"Immediate attention required.",
                notification_type=NotificationType.ERROR,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.PRP,
                notification_data={
                    "checklist_id": checklist.id,
                    "checklist_code": checklist.checklist_code,
                    "failed_items": checklist.failed_items,
                    "total_items": checklist.total_items,
                    "compliance_percentage": checklist.compliance_percentage,
                    "severity": severity
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.warning(f"Non-conformance created for checklist {checklist.checklist_code}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create non-conformance for checklist {checklist.id}: {str(e)}")
            return False
    
    def check_overdue_checklists(self) -> List[PRPChecklist]:
        """Check for overdue checklists and create escalation notifications"""
        
        overdue_checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.due_date < datetime.utcnow(),
                PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
            )
        ).all()
        
        for checklist in overdue_checklists:
            self._create_escalation_notification(checklist)
        
        return overdue_checklists
    
    def _create_escalation_notification(self, checklist: PRPChecklist):
        """Create escalation notification for overdue checklist"""
        
        try:
            # Calculate days overdue
            days_overdue = (datetime.utcnow() - checklist.due_date).days
            
            # Get program details
            program = self.db.query(PRPProgram).filter(PRPProgram.id == checklist.program_id).first()
            
            # Create escalation notification
            notification = Notification(
                user_id=checklist.assigned_to,
                title=f"URGENT: Overdue PRP Checklist - {checklist.name}",
                message=f"Checklist '{checklist.name}' is {days_overdue} day(s) overdue. "
                       f"Program: {program.name if program else 'Unknown'}. "
                       f"Immediate action required to maintain compliance.",
                notification_type=NotificationType.ERROR,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.PRP,
                notification_data={
                    "checklist_id": checklist.id,
                    "checklist_code": checklist.checklist_code,
                    "days_overdue": days_overdue,
                    "program_name": program.name if program else "Unknown",
                    "escalation_type": "overdue"
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.warning(f"Escalation notification created for overdue checklist {checklist.checklist_code}")
            
        except Exception as e:
            logger.error(f"Failed to create escalation notification for checklist {checklist.id}: {str(e)}")
    
    def upload_evidence_file(self, checklist_id: int, file_data: bytes, filename: str, uploaded_by: int) -> Dict[str, Any]:
        """Upload evidence file for a checklist"""
        
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"evidence_{checklist_id}_{uuid.uuid4().hex}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Update checklist evidence files
            checklist = self.db.query(PRPChecklist).filter(PRPChecklist.id == checklist_id).first()
            if checklist:
                evidence_files = []
                if checklist.evidence_files:
                    try:
                        evidence_files = json.loads(checklist.evidence_files)
                    except:
                        evidence_files = []
                
                evidence_files.append({
                    "type": "evidence",
                    "original_filename": filename,
                    "filename": unique_filename,
                    "file_path": file_path,
                    "file_size": len(file_data),
                    "uploaded_by": uploaded_by,
                    "uploaded_at": datetime.utcnow().isoformat()
                })
                
                checklist.evidence_files = json.dumps(evidence_files)
                self.db.commit()
            
            return {
                "file_id": unique_filename,
                "filename": unique_filename,
                "file_path": file_path,
                "file_size": len(file_data),
                "file_type": file_extension,
                "uploaded_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to upload evidence file for checklist {checklist_id}: {str(e)}")
            raise ValueError(f"Failed to upload file: {str(e)}")
    
    def get_prp_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive PRP dashboard statistics"""
        
        # Get total programs
        total_programs = self.db.query(PRPProgram).count()
        
        # Get active programs
        active_programs = self.db.query(PRPProgram).filter(PRPProgram.status == PRPStatus.ACTIVE).count()
        
        # Get total checklists
        total_checklists = self.db.query(PRPChecklist).count()
        
        # Get pending checklists
        pending_checklists = self.db.query(PRPChecklist).filter(
            PRPChecklist.status == ChecklistStatus.PENDING
        ).count()
        
        # Get overdue checklists
        overdue_checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.due_date < datetime.utcnow(),
                PRPChecklist.status.in_([ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS])
            )
        ).count()
        
        # Get completed checklists this month
        current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        completed_this_month = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.status == ChecklistStatus.COMPLETED,
                PRPChecklist.completed_date >= current_month_start
            )
        ).count()
        
        # Calculate compliance rate
        completed_checklists = self.db.query(PRPChecklist).filter(
            PRPChecklist.status == ChecklistStatus.COMPLETED
        ).all()
        
        total_compliance = sum(checklist.compliance_percentage for checklist in completed_checklists)
        compliance_rate = total_compliance / len(completed_checklists) if completed_checklists else 0.0
        
        # Get recent checklists
        recent_checklists = self.db.query(PRPChecklist).order_by(
            desc(PRPChecklist.scheduled_date)
        ).limit(5).all()
        
        # Get upcoming checklists
        upcoming_checklists = self.db.query(PRPChecklist).filter(
            and_(
                PRPChecklist.scheduled_date >= datetime.utcnow(),
                PRPChecklist.status == ChecklistStatus.PENDING
            )
        ).order_by(PRPChecklist.scheduled_date).limit(5).all()
        
        return {
            "total_programs": total_programs,
            "active_programs": active_programs,
            "total_checklists": total_checklists,
            "pending_checklists": pending_checklists,
            "overdue_checklists": overdue_checklists,
            "completed_this_month": completed_this_month,
            "compliance_rate": compliance_rate,
            "recent_checklists": [
                {
                    "id": checklist.id,
                    "name": checklist.name,
                    "status": checklist.status.value if checklist.status else None,
                    "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
                    "compliance_percentage": checklist.compliance_percentage,
                } for checklist in recent_checklists
            ],
            "upcoming_checklists": [
                {
                    "id": checklist.id,
                    "name": checklist.name,
                    "scheduled_date": checklist.scheduled_date.isoformat() if checklist.scheduled_date else None,
                    "assigned_to": checklist.assigned_to,
                } for checklist in upcoming_checklists
            ]
        }
    
    def generate_prp_report(self, program_id: Optional[int] = None, 
                          category: Optional[PRPCategory] = None,
                          date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate PRP report data"""
        
        query = self.db.query(PRPChecklist)
        
        if program_id:
            query = query.filter(PRPChecklist.program_id == program_id)
        
        if date_from:
            query = query.filter(PRPChecklist.scheduled_date >= date_from)
        
        if date_to:
            query = query.filter(PRPChecklist.scheduled_date <= date_to)
        
        checklists = query.all()
        
        # Get program details if specified
        program_details = None
        if program_id:
            program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
            if program:
                program_details = {
                    "id": program.id,
                    "program_code": program.program_code,
                    "name": program.name,
                    "category": program.category.value,
                    "frequency": program.frequency.value,
                }
        
        # Calculate statistics
        total_checklists = len(checklists)
        completed_checklists = [c for c in checklists if c.status == ChecklistStatus.COMPLETED]
        failed_checklists = [c for c in checklists if c.status == ChecklistStatus.FAILED]
        overdue_checklists = [c for c in checklists if c.due_date < datetime.utcnow() and c.status in [ChecklistStatus.PENDING, ChecklistStatus.IN_PROGRESS]]
        
        avg_compliance = sum(c.compliance_percentage for c in completed_checklists) / len(completed_checklists) if completed_checklists else 0.0
        
        return {
            "program_details": program_details,
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
            },
            "statistics": {
                "total_checklists": total_checklists,
                "completed_checklists": len(completed_checklists),
                "failed_checklists": len(failed_checklists),
                "overdue_checklists": len(overdue_checklists),
                "average_compliance": avg_compliance,
            },
            "checklists": [
                {
                    "id": checklist.id,
                    "checklist_code": checklist.checklist_code,
                    "name": checklist.name,
                    "status": checklist.status.value,
                    "scheduled_date": checklist.scheduled_date.isoformat() if checklist.scheduled_date else None,
                    "due_date": checklist.due_date.isoformat() if checklist.due_date else None,
                    "completed_date": checklist.completed_date.isoformat() if checklist.completed_date else None,
                    "compliance_percentage": checklist.compliance_percentage,
                    "corrective_actions_required": checklist.corrective_actions_required,
                } for checklist in checklists
            ],
            "generated_at": datetime.utcnow().isoformat()
        } 