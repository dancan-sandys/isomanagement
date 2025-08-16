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
    RiskMatrix, RiskAssessment, RiskControl, CorrectiveAction, PreventiveAction,
    PRPCategory, PRPFrequency, PRPStatus, ChecklistStatus, RiskLevel, CorrectiveActionStatus
)
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.schemas.prp import (
    PRPProgramCreate, PRPProgramUpdate, ChecklistCreate, ChecklistUpdate,
    ChecklistItemCreate, ChecklistCompletion, NonConformanceCreate,
    ReminderCreate, ScheduleCreate, ResponseType, RiskMatrixCreate,
    RiskAssessmentCreate, RiskControlCreate, CorrectiveActionCreate, PreventiveActionCreate
)

logger = logging.getLogger(__name__)


class PRPService:
    """
    Enhanced service for handling PRP business logic with ISO 22002-1:2025 compliance
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = "uploads/prp"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def create_prp_program(self, program_data: PRPProgramCreate, created_by: int) -> PRPProgram:
        """Create a new PRP program with ISO 22002-1:2025 compliance"""
        
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
            risk_assessment_required=program_data.risk_assessment_required if hasattr(program_data, 'risk_assessment_required') else True,
            frequency=program_data.frequency,
            frequency_details=program_data.frequency_details,
            next_due_date=next_due_date,
            sop_reference=program_data.sop_reference,
            forms_required=program_data.forms_required,
            records_required=program_data.records_required,
            training_requirements=program_data.training_requirements,
            monitoring_frequency=program_data.monitoring_frequency,
            verification_frequency=program_data.verification_frequency,
            acceptance_criteria=program_data.acceptance_criteria,
            trend_analysis_required=program_data.trend_analysis_required,
            corrective_action_procedure=program_data.corrective_action_procedure,
            escalation_procedure=program_data.escalation_procedure,
            preventive_action_procedure=program_data.preventive_action_procedure,
            created_by=created_by
        )
        
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        
        return program
    
    def create_risk_matrix(self, matrix_data: RiskMatrixCreate, created_by: int) -> RiskMatrix:
        """Create a new risk matrix for PRP risk assessment"""
        
        matrix = RiskMatrix(
            name=matrix_data.name,
            description=matrix_data.description,
            likelihood_levels=matrix_data.likelihood_levels,
            severity_levels=matrix_data.severity_levels,
            risk_levels=matrix_data.risk_levels,
            created_by=created_by
        )
        
        self.db.add(matrix)
        self.db.commit()
        self.db.refresh(matrix)
        
        return matrix
    
    def create_risk_assessment(self, program_id: int, assessment_data: RiskAssessmentCreate, created_by: int) -> RiskAssessment:
        """Create a new risk assessment for a PRP program"""
        
        # Verify program exists
        program = self.db.query(PRPProgram).filter(PRPProgram.id == program_id).first()
        if not program:
            raise ValueError("PRP program not found")
        
        # Calculate risk score and level
        risk_score, risk_level = self._calculate_risk_score(
            assessment_data.likelihood_level,
            assessment_data.severity_level
        )
        
        assessment = RiskAssessment(
            program_id=program_id,
            assessment_code=assessment_data.assessment_code,
            hazard_identified=assessment_data.hazard_identified,
            hazard_description=assessment_data.hazard_description,
            likelihood_level=assessment_data.likelihood_level,
            severity_level=assessment_data.severity_level,
            risk_level=risk_level,
            risk_score=risk_score,
            acceptability=risk_level in [RiskLevel.VERY_LOW, RiskLevel.LOW],
            existing_controls=assessment_data.existing_controls,
            additional_controls_required=assessment_data.additional_controls_required,
            control_effectiveness=assessment_data.control_effectiveness,
            created_by=created_by
        )
        
        self.db.add(assessment)
        self.db.commit()
        self.db.refresh(assessment)
        
        return assessment
    
    def _calculate_risk_score(self, likelihood: str, severity: str) -> Tuple[int, RiskLevel]:
        """Calculate risk score and level based on likelihood and severity"""
        
        # Define scoring matrix (can be made configurable)
        likelihood_scores = {
            "Rare": 1,
            "Unlikely": 2,
            "Possible": 3,
            "Likely": 4,
            "Certain": 5
        }
        
        severity_scores = {
            "Negligible": 1,
            "Minor": 2,
            "Moderate": 3,
            "Major": 4,
            "Catastrophic": 5
        }
        
        likelihood_score = likelihood_scores.get(likelihood, 3)
        severity_score = severity_scores.get(severity, 3)
        risk_score = likelihood_score * severity_score
        
        # Determine risk level
        if risk_score <= 4:
            risk_level = RiskLevel.VERY_LOW
        elif risk_score <= 8:
            risk_level = RiskLevel.LOW
        elif risk_score <= 12:
            risk_level = RiskLevel.MEDIUM
        elif risk_score <= 16:
            risk_level = RiskLevel.HIGH
        elif risk_score <= 20:
            risk_level = RiskLevel.VERY_HIGH
        else:
            risk_level = RiskLevel.CRITICAL
        
        return risk_score, risk_level
    
    def create_corrective_action(self, action_data: CorrectiveActionCreate, created_by: int) -> CorrectiveAction:
        """Create a new corrective action"""
        
        action = CorrectiveAction(
            action_code=action_data.action_code,
            source_type=action_data.source_type,
            source_id=action_data.source_id,
            checklist_id=action_data.checklist_id,
            program_id=action_data.program_id,
            non_conformance_description=action_data.non_conformance_description,
            non_conformance_date=action_data.non_conformance_date,
            severity=action_data.severity,
            immediate_cause=action_data.immediate_cause,
            root_cause_analysis=action_data.root_cause_analysis,
            root_cause_category=action_data.root_cause_category,
            action_description=action_data.action_description,
            action_type=action_data.action_type,
            responsible_person=action_data.responsible_person,
            assigned_to=action_data.assigned_to,
            target_completion_date=action_data.target_completion_date,
            effectiveness_criteria=action_data.effectiveness_criteria,
            created_by=created_by
        )
        
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        # Create notification for assigned person
        self._create_action_notification(action, "corrective_action_assigned")
        
        return action
    
    def create_preventive_action(self, action_data: PreventiveActionCreate, created_by: int) -> PreventiveAction:
        """Create a new preventive action"""
        
        action = PreventiveAction(
            action_code=action_data.action_code,
            trigger_type=action_data.trigger_type,
            trigger_description=action_data.trigger_description,
            program_id=action_data.program_id,
            action_description=action_data.action_description,
            objective=action_data.objective,
            responsible_person=action_data.responsible_person,
            assigned_to=action_data.assigned_to,
            implementation_plan=action_data.implementation_plan,
            resources_required=action_data.resources_required,
            budget_estimate=action_data.budget_estimate,
            planned_start_date=action_data.planned_start_date,
            planned_completion_date=action_data.planned_completion_date,
            success_criteria=action_data.success_criteria,
            created_by=created_by
        )
        
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        
        # Create notification for assigned person
        self._create_action_notification(action, "preventive_action_assigned")
        
        return action
    
    def _create_action_notification(self, action, notification_type: str):
        """Create notification for action assignment"""
        
        try:
            if notification_type == "corrective_action_assigned":
                title = f"Corrective Action Assigned: {action.action_code}"
                message = f"You have been assigned a corrective action: {action.action_description}"
            else:
                title = f"Preventive Action Assigned: {action.action_code}"
                message = f"You have been assigned a preventive action: {action.action_description}"
            
            notification = Notification(
                user_id=action.assigned_to,
                title=title,
                message=message,
                notification_type=NotificationType.INFO,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.PRP,
                notification_data={
                    "action_id": action.id,
                    "action_code": action.action_code,
                    "action_type": notification_type,
                    "target_date": action.target_completion_date.isoformat() if hasattr(action, 'target_completion_date') else None
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create action notification: {str(e)}")
    
    def get_prp_compliance_report(self, program_id: Optional[int] = None, 
                                date_from: Optional[datetime] = None,
                                date_to: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate comprehensive PRP compliance report"""
        
        query = self.db.query(PRPProgram)
        if program_id:
            query = query.filter(PRPProgram.id == program_id)
        
        programs = query.all()
        
        report_data = {
            "generated_at": datetime.utcnow().isoformat(),
            "period": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None
            },
            "programs": [],
            "summary": {
                "total_programs": len(programs),
                "active_programs": 0,
                "programs_with_risk_assessments": 0,
                "programs_with_corrective_actions": 0,
                "overall_compliance_rate": 0.0
            }
        }
        
        total_compliance = 0.0
        program_count = 0
        
        for program in programs:
            # Get program statistics
            checklist_count = self.db.query(PRPChecklist).filter(
                PRPChecklist.program_id == program.id
            ).count()
            
            completed_checklists = self.db.query(PRPChecklist).filter(
                and_(
                    PRPChecklist.program_id == program.id,
                    PRPChecklist.status == ChecklistStatus.COMPLETED
                )
            ).all()
            
            risk_assessment_count = self.db.query(RiskAssessment).filter(
                RiskAssessment.program_id == program.id
            ).count()
            
            corrective_action_count = self.db.query(CorrectiveAction).filter(
                CorrectiveAction.program_id == program.id
            ).count()
            
            # Calculate compliance rate
            compliance_rate = 0.0
            if completed_checklists:
                total_items = sum(c.total_items for c in completed_checklists)
                passed_items = sum(c.passed_items for c in completed_checklists)
                if total_items > 0:
                    compliance_rate = (passed_items / total_items) * 100
            
            total_compliance += compliance_rate
            program_count += 1
            
            # Update summary
            if program.status == PRPStatus.ACTIVE:
                report_data["summary"]["active_programs"] += 1
            if risk_assessment_count > 0:
                report_data["summary"]["programs_with_risk_assessments"] += 1
            if corrective_action_count > 0:
                report_data["summary"]["programs_with_corrective_actions"] += 1
            
            program_data = {
                "id": program.id,
                "program_code": program.program_code,
                "name": program.name,
                "category": program.category.value,
                "status": program.status.value,
                "risk_level": program.risk_level.value if program.risk_level else None,
                "checklist_count": checklist_count,
                "completed_checklists": len(completed_checklists),
                "compliance_rate": compliance_rate,
                "risk_assessment_count": risk_assessment_count,
                "corrective_action_count": corrective_action_count,
                "last_review_date": program.last_review_date.isoformat() if program.last_review_date else None,
                "next_review_date": program.next_review_date.isoformat() if program.next_review_date else None
            }
            
            report_data["programs"].append(program_data)
        
        # Calculate overall compliance
        if program_count > 0:
            report_data["summary"]["overall_compliance_rate"] = total_compliance / program_count
        
        return report_data
    
    def get_risk_assessment_summary(self, program_id: Optional[int] = None) -> Dict[str, Any]:
        """Get risk assessment summary for PRP programs"""
        
        query = self.db.query(RiskAssessment)
        if program_id:
            query = query.filter(RiskAssessment.program_id == program_id)
        
        assessments = query.all()
        
        risk_level_counts = {
            RiskLevel.VERY_LOW.value: 0,
            RiskLevel.LOW.value: 0,
            RiskLevel.MEDIUM.value: 0,
            RiskLevel.HIGH.value: 0,
            RiskLevel.VERY_HIGH.value: 0,
            RiskLevel.CRITICAL.value: 0
        }
        
        for assessment in assessments:
            if assessment.risk_level:
                risk_level_counts[assessment.risk_level.value] += 1
        
        return {
            "total_assessments": len(assessments),
            "risk_level_distribution": risk_level_counts,
            "high_risk_count": risk_level_counts[RiskLevel.HIGH.value] + 
                              risk_level_counts[RiskLevel.VERY_HIGH.value] + 
                              risk_level_counts[RiskLevel.CRITICAL.value],
            "assessments_requiring_controls": len([a for a in assessments if not a.acceptability])
        }
    
    def get_corrective_action_summary(self, program_id: Optional[int] = None) -> Dict[str, Any]:
        """Get corrective action summary for PRP programs"""
        
        query = self.db.query(CorrectiveAction)
        if program_id:
            query = query.filter(CorrectiveAction.program_id == program_id)
        
        actions = query.all()
        
        status_counts = {
            CorrectiveActionStatus.OPEN.value: 0,
            CorrectiveActionStatus.IN_PROGRESS.value: 0,
            CorrectiveActionStatus.PENDING_VERIFICATION.value: 0,
            CorrectiveActionStatus.VERIFIED.value: 0,
            CorrectiveActionStatus.CLOSED.value: 0,
            CorrectiveActionStatus.ESCALATED.value: 0
        }
        
        for action in actions:
            status_counts[action.status.value] += 1
        
        overdue_actions = [a for a in actions if a.target_completion_date and 
                          a.target_completion_date < datetime.utcnow() and 
                          a.status not in [CorrectiveActionStatus.CLOSED, CorrectiveActionStatus.VERIFIED]]
        
        return {
            "total_actions": len(actions),
            "status_distribution": status_counts,
            "overdue_actions": len(overdue_actions),
            "open_actions": status_counts[CorrectiveActionStatus.OPEN.value] + 
                           status_counts[CorrectiveActionStatus.IN_PROGRESS.value]
        }
    
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
            item = self.db.query(PRPChecklistItem).filter(PRPChecklistItem.id == item_completion["item_id"]).first()
            if item:
                item.response = item_completion["response"]
                item.response_value = item_completion.get("response_value")
                item.is_compliant = item_completion["is_compliant"]
                item.comments = item_completion.get("comments")
                item.evidence_files = item_completion.get("evidence_files")
                item.updated_at = datetime.utcnow()
                
                total_items += 1
                if item_completion["is_compliant"]:
                    passed_items += 1
                else:
                    failed_items += 1
                
                # Check if item is not applicable
                if item_completion["response"].lower() in ['n/a', 'not applicable', 'na']:
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
            
            # Store signature metadata in database
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
        
        # Get risk assessment summary
        risk_summary = self.get_risk_assessment_summary()
        
        # Get corrective action summary
        action_summary = self.get_corrective_action_summary()
        
        return {
            "total_programs": total_programs,
            "active_programs": active_programs,
            "total_checklists": total_checklists,
            "pending_checklists": pending_checklists,
            "overdue_checklists": overdue_checklists,
            "completed_this_month": completed_this_month,
            "compliance_rate": compliance_rate,
            "risk_assessment_summary": risk_summary,
            "corrective_action_summary": action_summary,
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