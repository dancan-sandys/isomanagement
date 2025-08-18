import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import uuid
from enum import Enum

from app.models.haccp import (
    Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog,
    HazardType, RiskLevel, CCPStatus,
    HACCPPlan, HACCPPlanVersion, HACCPPlanApproval, HACCPPlanStatus,
    ProductRiskConfig, DecisionTree, HazardReview
)
from app.models.notification import Notification, NotificationType, NotificationPriority, NotificationCategory
from app.models.user import User
from app.schemas.haccp import (
    ProductCreate, ProductUpdate, ProcessFlowCreate, HazardCreate, CCPCreate,
    MonitoringLogCreate, VerificationLogCreate, DecisionTreeResult, DecisionTreeStep,
    DecisionTreeQuestion, FlowchartData, FlowchartNode, FlowchartEdge
)
from app.models.training import RoleRequiredTraining, TrainingAttendance, TrainingSession, TrainingCertificate, HACCPRequiredTraining, TrainingAction
from app.models.traceability import Batch
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from app.models.haccp import CCPMonitoringSchedule
from app.schemas.haccp import MonitoringScheduleStatus
from app.models.equipment import Equipment
from app.models.haccp import CCPVerificationProgram, CCPValidation
from app.models.haccp import HACCPAuditLog, HACCPEvidenceAttachment
from app.models.document import Document

logger = logging.getLogger(__name__)


class HACCPValidationError(Exception):
    """Custom exception for HACCP validation errors"""
    pass


class HACCPBusinessError(Exception):
    """Custom exception for HACCP business logic errors"""
    pass


class HACCPActionType(Enum):
    """Enum for HACCP action types"""
    MONITOR = "monitor"
    VERIFY = "verify"
    VALIDATE = "validate"
    REVIEW = "review"
    APPROVE = "approve"


class HACCPValidationService:
    """Service for HACCP data validation"""
    
    @staticmethod
    def validate_risk_assessment(likelihood: int, severity: int) -> None:
        """Validate risk assessment parameters"""
        if not (1 <= likelihood <= 5):
            raise HACCPValidationError("Likelihood must be between 1 and 5")
        if not (1 <= severity <= 5):
            raise HACCPValidationError("Severity must be between 1 and 5")
    
    @staticmethod
    def validate_critical_limits(critical_limits: Dict[str, Any]) -> None:
        """Validate critical limits data"""
        if not critical_limits:
            raise HACCPValidationError("Critical limits cannot be empty")
        
        required_fields = ['parameter', 'min_value', 'max_value', 'unit']
        for field in required_fields:
            if field not in critical_limits:
                raise HACCPValidationError(f"Critical limit missing required field: {field}")
    
    @staticmethod
    def validate_monitoring_schedule(schedule_data: Dict[str, Any]) -> None:
        """Validate monitoring schedule data"""
        if not schedule_data.get('frequency'):
            raise HACCPValidationError("Monitoring frequency is required")
        
        valid_frequencies = ['hourly', 'daily', 'weekly', 'monthly', 'quarterly']
        if schedule_data['frequency'] not in valid_frequencies:
            raise HACCPValidationError(f"Invalid frequency. Must be one of: {valid_frequencies}")


class HACCPNotificationService:
    """Service for HACCP notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def notify_ccp_deviation(self, ccp_id: int, deviation_details: str, user_id: int) -> None:
        """Notify relevant users about CCP deviation"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            return
        
        # Notify HACCP team members
        haccp_users = self.db.query(User).filter(User.role.has(name="HACCP Team")).all()
        
        for user in haccp_users:
            notification = Notification(
                user_id=user.id,
                type=NotificationType.ALERT,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.HACCP,
                title="CCP Deviation Detected",
                message=f"CCP '{ccp.name}' has a deviation: {deviation_details}",
                data={
                    "ccp_id": ccp_id,
                    "deviation_details": deviation_details,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            self.db.add(notification)
        
        self.db.commit()
    
    def notify_overdue_monitoring(self, ccp_id: int) -> None:
        """Notify about overdue monitoring"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            return
        
        # Notify assigned monitors
        assigned_users = self.db.query(User).join(CCPMonitoringSchedule).filter(
            CCPMonitoringSchedule.ccp_id == ccp_id
        ).all()
        
        for user in assigned_users:
            notification = Notification(
                user_id=user.id,
                type=NotificationType.REMINDER,
                priority=NotificationPriority.MEDIUM,
                category=NotificationCategory.HACCP,
                title="Overdue CCP Monitoring",
                message=f"Monitoring for CCP '{ccp.name}' is overdue",
                data={
                    "ccp_id": ccp_id,
                    "overdue_since": datetime.utcnow().isoformat()
                }
            )
            self.db.add(notification)
        
        self.db.commit()


class HACCPAuditService:
    """Service for HACCP audit logging"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_haccp_action(self, action_type: str, record_type: str, record_id: int, 
                        user_id: int, details: Dict[str, Any] = None) -> HACCPAuditLog:
        """Log HACCP actions for audit trail"""
        audit_log = HACCPAuditLog(
            event_type=action_type,
            event_description=f"{action_type.title()} action on {record_type}",
            record_type=record_type,
            record_id=record_id,
            user_id=user_id,
            old_values=json.dumps(details.get('old_values', {})) if details else None,
            new_values=json.dumps(details.get('new_values', {})) if details else None,
            changed_fields=json.dumps(details.get('changed_fields', [])) if details else None,
            ip_address=details.get('ip_address'),
            user_agent=details.get('user_agent'),
            session_id=details.get('session_id')
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log


class HACCPRiskCalculationService:
    """Service for HACCP risk calculations"""
    
    @staticmethod
    def calculate_risk_score(likelihood: int, severity: int) -> int:
        """Calculate risk score based on likelihood and severity"""
        return likelihood * severity
    
    @staticmethod
    def determine_risk_level(risk_score: int, product_config: Optional[ProductRiskConfig] = None) -> RiskLevel:
        """Determine risk level based on score and product configuration"""
        if product_config:
            if risk_score <= product_config.low_threshold:
                return RiskLevel.LOW
            elif risk_score <= product_config.medium_threshold:
                return RiskLevel.MEDIUM
            elif risk_score <= product_config.high_threshold:
                return RiskLevel.HIGH
            else:
                return RiskLevel.CRITICAL
        else:
            # Default thresholds
            if risk_score <= 4:
                return RiskLevel.LOW
            elif risk_score <= 8:
                return RiskLevel.MEDIUM
            elif risk_score <= 15:
                return RiskLevel.HIGH
            else:
                return RiskLevel.CRITICAL


class HACCPService:
    """
    Enhanced service for handling HACCP business logic with consolidated functionality
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.validation_service = HACCPValidationService()
        self.notification_service = HACCPNotificationService(db)
        self.audit_service = HACCPAuditService(db)
        self.risk_service = HACCPRiskCalculationService()

    def user_has_required_training(self, user_id: int, action: str, *, ccp_id: int | None = None, equipment_id: int | None = None) -> bool:
        """
        Check if a user meets competency (training) requirements for a given HACCP action.
        Action can be "monitor" or "verify". Uses RoleRequiredTraining as configuration:
        - If the user's role has mandatory trainings defined, require completion (attendance or certificate)
          for all those programs.
        - If no role requirements exist, return True (no configured requirements).
        """
        try:
            user: Optional[User] = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.role_id:
                return False

            required_program_ids: set[int] = set()
            # Prefer action/CCP/equipment-scoped HACCP requirements if available
            try:
                scoped_q = self.db.query(HACCPRequiredTraining).filter(
                    HACCPRequiredTraining.role_id == user.role_id,
                    HACCPRequiredTraining.action == TrainingAction(action) if action else TrainingAction.MONITOR,
                    HACCPRequiredTraining.is_mandatory == True,
                )
                if ccp_id is not None:
                    scoped_q = scoped_q.filter(
                        (HACCPRequiredTraining.ccp_id == ccp_id) | (HACCPRequiredTraining.ccp_id.is_(None))
                    )
                if equipment_id is not None:
                    scoped_q = scoped_q.filter(
                        (HACCPRequiredTraining.equipment_id == equipment_id) | (HACCPRequiredTraining.equipment_id.is_(None))
                    )
                scoped_records = scoped_q.all()
                # If any record exists with specific scoping, keep only the most specific ones
                specific = [r for r in scoped_records if (r.ccp_id is not None) or (r.equipment_id is not None)]
                chosen = specific if specific else scoped_records
                required_program_ids = {r.program_id for r in chosen}
            except (SQLAlchemyError, OperationalError):
                # Table may not exist yet; ignore and fall back to role-level
                required_program_ids = set()

            if not required_program_ids:
                # Fallback to role-wide requirements
                try:
                    required_records = self.db.query(RoleRequiredTraining).filter(
                        RoleRequiredTraining.role_id == user.role_id,
                        RoleRequiredTraining.is_mandatory == True,
                    ).all()
                    required_program_ids = {rec.program_id for rec in required_records}
                except (SQLAlchemyError, OperationalError):
                    required_program_ids = set()

            if not required_program_ids:
                return True  # No requirements configured => allow

            # Compute set of program_ids the user has completed via attendance or certificates
            # Attendance-based completion
            attended_program_ids = {
                pid for (pid,) in self.db.query(TrainingSession.program_id)
                    .join(TrainingAttendance, TrainingAttendance.session_id == TrainingSession.id)
                    .filter(
                        TrainingAttendance.user_id == user_id,
                        TrainingAttendance.status == "completed"
                    )
            }

            # Certificate-based completion
            certified_program_ids = {
                pid for (pid,) in self.db.query(TrainingCertificate.program_id)
                    .filter(
                        TrainingCertificate.user_id == user_id,
                        TrainingCertificate.status == "valid"
                    )
            }

            completed_program_ids = attended_program_ids | certified_program_ids
            return required_program_ids.issubset(completed_program_ids)
            
        except Exception as e:
            logger.error(f"Error checking user training requirements: {e}")
            return False
    
    def create_product(self, product_data: ProductCreate, created_by: int) -> Product:
        """Create a new product"""
        
        # Check if product code already exists
        existing_product = self.db.query(Product).filter(
            Product.product_code == product_data.product_code
        ).first()
        
        if existing_product:
            raise ValueError("Product code already exists")
        
        product = Product(
            product_code=product_data.product_code,
            name=product_data.name,
            description=product_data.description,
            category=product_data.category,
            formulation=product_data.formulation,
            allergens=product_data.allergens,
            shelf_life_days=product_data.shelf_life_days,
            storage_conditions=product_data.storage_conditions,
            packaging_type=product_data.packaging_type,
            created_by=created_by
        )
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def create_process_flow(self, product_id: int, flow_data: ProcessFlowCreate, created_by: int) -> ProcessFlow:
        """Create a process flow step"""
        
        # Verify product exists
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        process_flow = ProcessFlow(
            product_id=product_id,
            step_number=flow_data.step_number,
            step_name=flow_data.step_name,
            description=flow_data.description,
            equipment=flow_data.equipment,
            temperature=flow_data.temperature,
            time_minutes=flow_data.time_minutes,
            ph=flow_data.ph,
            aw=flow_data.aw,
            parameters=flow_data.parameters,
            created_by=created_by
        )
        
        self.db.add(process_flow)
        self.db.commit()
        self.db.refresh(process_flow)
        
        return process_flow

    def delete_product(self, product_id: int, deleted_by: int) -> bool:
        """Delete a product and all dependent HACCP records in a safe order.

        This avoids NOT NULL/foreign-key violations on SQLite by explicitly
        deleting child rows before the parent product.
        """
        product: Optional[Product] = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")

        try:
            # Collect related ids
            ccp_ids = [cid for (cid,) in self.db.query(CCP.id).filter(CCP.product_id == product_id).all()]
            hazard_ids = [hid for (hid,) in self.db.query(Hazard.id).filter(Hazard.product_id == product_id).all()]
            plan_ids = [pid for (pid,) in self.db.query(HACCPPlan.id).filter(HACCPPlan.product_id == product_id).all()]

            # Delete CCP-related artifacts first (logs, schedules, programs, validations, attachments)
            if ccp_ids:
                # Logs
                self.db.query(CCPVerificationLog).filter(CCPVerificationLog.ccp_id.in_(ccp_ids)).delete(synchronize_session=False)
                self.db.query(CCPMonitoringLog).filter(CCPMonitoringLog.ccp_id.in_(ccp_ids)).delete(synchronize_session=False)
                # Programs/Schedules/Validations
                try:
                    self.db.query(CCPVerificationProgram).filter(CCPVerificationProgram.ccp_id.in_(ccp_ids)).delete(synchronize_session=False)
                except Exception:
                    pass
                try:
                    self.db.query(CCPMonitoringSchedule).filter(CCPMonitoringSchedule.ccp_id.in_(ccp_ids)).delete(synchronize_session=False)
                except Exception:
                    pass
                try:
                    self.db.query(CCPValidation).filter(CCPValidation.ccp_id.in_(ccp_ids)).delete(synchronize_session=False)
                except Exception:
                    pass

            # Delete hazard-related artifacts (decision trees, reviews) then hazards
            if hazard_ids:
                self.db.query(DecisionTree).filter(DecisionTree.hazard_id.in_(hazard_ids)).delete(synchronize_session=False)
                try:
                    self.db.query(HazardReview).filter(HazardReview.hazard_id.in_(hazard_ids)).delete(synchronize_session=False)
                except Exception:
                    pass
                self.db.query(Hazard).filter(Hazard.id.in_(hazard_ids)).delete(synchronize_session=False)

            # Delete process flows for this product
            self.db.query(ProcessFlow).filter(ProcessFlow.product_id == product_id).delete(synchronize_session=False)

            # Delete HACCP plans (versions and approvals first)
            if plan_ids:
                self.db.query(HACCPPlanApproval).filter(HACCPPlanApproval.plan_id.in_(plan_ids)).delete(synchronize_session=False)
                self.db.query(HACCPPlanVersion).filter(HACCPPlanVersion.plan_id.in_(plan_ids)).delete(synchronize_session=False)
                self.db.query(HACCPPlan).filter(HACCPPlan.id.in_(plan_ids)).delete(synchronize_session=False)

            # Delete product-specific risk config
            self.db.query(ProductRiskConfig).filter(ProductRiskConfig.product_id == product_id).delete(synchronize_session=False)

            # Finally delete CCPs and the Product
            if ccp_ids:
                self.db.query(CCP).filter(CCP.id.in_(ccp_ids)).delete(synchronize_session=False)

            self.db.delete(product)
            self.db.commit()

            # Audit (best effort)
            try:
                self.audit_service.log_event(
                    user_id=deleted_by,
                    event_type="haccp_product_deleted",
                    record_type="haccp_product",
                    record_id=str(product_id),
                    description="Product and dependent HACCP records deleted",
                )
            except Exception:
                pass

            return True

        except Exception:
            self.db.rollback()
            raise
    
    def create_hazard(self, product_id: int, hazard_data: HazardCreate, created_by: int) -> Hazard:
        """Create a hazard with product-specific risk assessment (ISO 22000 compliant)"""
        
        # Verify product exists
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Get product-specific risk configuration
        risk_config = self.db.query(ProductRiskConfig).filter(ProductRiskConfig.product_id == product_id).first()
        
        # Calculate risk score using product-specific configuration
        likelihood = hazard_data.likelihood
        severity = hazard_data.severity
        
        if risk_config:
            # Use product-specific risk calculation
            risk_score = risk_config.get_risk_score(likelihood, severity)
            risk_level_str = risk_config.calculate_risk_level(likelihood, severity)
            
            # Convert string risk level to enum
            if risk_level_str == "low":
                risk_level = RiskLevel.LOW
            elif risk_level_str == "medium":
                risk_level = RiskLevel.MEDIUM
            elif risk_level_str == "high":
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL
        else:
            # Default risk calculation if no product-specific config exists
            risk_score = likelihood * severity
            if risk_score <= 4:
                risk_level = RiskLevel.LOW
            elif risk_score <= 8:
                risk_level = RiskLevel.MEDIUM
            elif risk_score <= 15:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL
        
        hazard = Hazard(
            product_id=product_id,
            process_step_id=hazard_data.process_step_id,
            hazard_type=hazard_data.hazard_type,
            hazard_name=hazard_data.hazard_name,
            description=hazard_data.description,
            rationale=hazard_data.rationale,  # New field for hazard analysis
            prp_reference_ids=hazard_data.prp_reference_ids,  # New field for PRP references
            reference_documents=hazard_data.references,  # New field for reference documents
            likelihood=likelihood,
            severity=severity,
            risk_score=risk_score,
            risk_level=risk_level,
            control_measures=hazard_data.control_measures,
            is_controlled=hazard_data.is_controlled,
            control_effectiveness=hazard_data.control_effectiveness,
            is_ccp=hazard_data.is_ccp,
            ccp_justification=hazard_data.ccp_justification,
            created_by=created_by
        )
        
        self.db.add(hazard)
        self.db.commit()
        self.db.refresh(hazard)
        
        return hazard
    
    def run_decision_tree(self, hazard_id: int, run_by_user_id: Optional[int] = None) -> DecisionTreeResult:
        """
        Run the CCP decision tree for a hazard
        Based on Codex Alimentarius decision tree
        """
        
        hazard = self.db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise ValueError("Hazard not found")
        
        steps = []
        is_ccp = False
        justification = ""
        
        # Question 1: Is control at this step necessary for safety?
        # Use product-specific risk configuration to determine if risk is high enough to require control
        risk_config = self.db.query(ProductRiskConfig).filter(ProductRiskConfig.product_id == hazard.product_id).first()
        
        # Use product-specific medium threshold if available, otherwise use default
        medium_threshold = 8  # Default
        if risk_config:
            medium_threshold = risk_config.medium_threshold
        
        # Use medium threshold as the cutoff for requiring control
        control_threshold = risk_config.medium_threshold if risk_config else 8
        q1_answer = hazard.risk_score >= control_threshold
        steps.append(DecisionTreeStep(
            question=DecisionTreeQuestion.Q1,
            answer=q1_answer,
            explanation=f"Risk score: {hazard.risk_score} (Control required if >= {control_threshold})"
        ))
        
        if not q1_answer:
            justification = "Control at this step is not necessary for safety"
            return DecisionTreeResult(is_ccp=False, justification=justification, steps=steps)
        
        # Question 2: Is it likely that contamination may occur or increase?
        q2_answer = hazard.likelihood >= 3  # Medium or higher likelihood
        steps.append(DecisionTreeStep(
            question=DecisionTreeQuestion.Q2,
            answer=q2_answer,
            explanation=f"Likelihood: {hazard.likelihood}/5 (Medium or higher likelihood of contamination)"
        ))
        
        if not q2_answer:
            justification = "Contamination is unlikely to occur or increase at this step"
            return DecisionTreeResult(is_ccp=False, justification=justification, steps=steps)
        
        # Question 3: Will a subsequent step eliminate or reduce the hazard?
        # Check if there are subsequent steps with control measures
        subsequent_steps = self.db.query(ProcessFlow).filter(
            and_(
                ProcessFlow.product_id == hazard.product_id,
                ProcessFlow.step_number > hazard.process_step.step_number
            )
        ).all()
        
        subsequent_hazards = self.db.query(Hazard).filter(
            and_(
                Hazard.product_id == hazard.product_id,
                Hazard.process_step_id.in_([step.id for step in subsequent_steps])
            )
        ).all()
        
        q3_answer = any(h.is_controlled for h in subsequent_hazards)
        steps.append(DecisionTreeStep(
            question=DecisionTreeQuestion.Q3,
            answer=q3_answer,
            explanation=f"Subsequent control measures: {'Yes' if q3_answer else 'No'}"
        ))
        
        # Question 4: Is this step specifically designed to eliminate or reduce the hazard?
        # Heuristic: mark True if current hazard is controlled at this step and effectiveness >=3
        q4_answer = bool(hazard.is_controlled and (hazard.control_effectiveness or 0) >= 3)
        steps.append(DecisionTreeStep(
            question=DecisionTreeQuestion.Q4,
            answer=q4_answer,
            explanation=(
                "This step is designed and effective to control the hazard"
                if q4_answer else "This step is not specifically designed or not effective enough"
            ),
        ))

        if q3_answer:
            justification = "A subsequent step will eliminate or reduce the hazard to acceptable levels"
            is_ccp = False
        elif q4_answer:
            justification = "This step is specifically designed to reduce the hazard – CCP"
            is_ccp = True
        else:
            justification = "No subsequent elimination/reduction and this step not designed – CCP"
            is_ccp = True

        # Persist outcome on hazard
        try:
            import json
            hazard.is_ccp = is_ccp
            hazard.ccp_justification = justification
            hazard.decision_tree_steps = json.dumps([
                {"question": s.question.value, "answer": s.answer, "explanation": s.explanation}
                for s in steps
            ])
            hazard.decision_tree_run_at = datetime.utcnow()
            hazard.decision_tree_by = run_by_user_id
            self.db.commit()
        except Exception:
            self.db.rollback()

        return DecisionTreeResult(is_ccp=is_ccp, justification=justification, steps=steps)

    def create_decision_tree(self, hazard_id: int, q1_answer: bool, q1_justification: str, user_id: int) -> DecisionTree:
        """Create a new decision tree for a hazard"""
        
        # Verify hazard exists
        hazard = self.db.query(Hazard).filter(Hazard.id == hazard_id).first()
        if not hazard:
            raise ValueError("Hazard not found")
        
        # Check if decision tree already exists
        existing_tree = self.db.query(DecisionTree).filter(DecisionTree.hazard_id == hazard_id).first()
        if existing_tree:
            raise ValueError("Decision tree already exists for this hazard")
        
        decision_tree = DecisionTree(
            hazard_id=hazard_id,
            q1_answer=q1_answer,
            q1_justification=q1_justification,
            q1_answered_by=user_id
        )
        
        # If Q1 is No, determine CCP decision immediately
        if not q1_answer:
            decision_tree.is_ccp = False
            decision_tree.decision_reasoning = "Q1: Control at this step is not necessary for safety"
            decision_tree.decision_date = datetime.utcnow()
            decision_tree.decision_by = user_id
            decision_tree.status = "completed"
        
        self.db.add(decision_tree)
        self.db.commit()
        self.db.refresh(decision_tree)
        
        return decision_tree
    
    def answer_decision_tree_question(self, hazard_id: int, question_number: int, answer: bool, justification: str, user_id: int) -> DecisionTree:
        """Answer a specific question in the decision tree"""
        
        decision_tree = self.db.query(DecisionTree).filter(DecisionTree.hazard_id == hazard_id).first()
        if not decision_tree:
            raise ValueError("Decision tree not found for this hazard")
        
        # Update the appropriate question
        if question_number == 1:
            decision_tree.q1_answer = answer
            decision_tree.q1_justification = justification
            decision_tree.q1_answered_by = user_id
            decision_tree.q1_answered_at = datetime.utcnow()
        elif question_number == 2:
            if not decision_tree.can_proceed_to_next_question():
                raise ValueError("Cannot answer Q2 - previous questions do not allow proceeding")
            decision_tree.q2_answer = answer
            decision_tree.q2_justification = justification
            decision_tree.q2_answered_by = user_id
            decision_tree.q2_answered_at = datetime.utcnow()
        elif question_number == 3:
            if not decision_tree.can_proceed_to_next_question():
                raise ValueError("Cannot answer Q3 - previous questions do not allow proceeding")
            decision_tree.q3_answer = answer
            decision_tree.q3_justification = justification
            decision_tree.q3_answered_by = user_id
            decision_tree.q3_answered_at = datetime.utcnow()
        elif question_number == 4:
            if not decision_tree.can_proceed_to_next_question():
                raise ValueError("Cannot answer Q4 - previous questions do not allow proceeding")
            decision_tree.q4_answer = answer
            decision_tree.q4_justification = justification
            decision_tree.q4_answered_by = user_id
            decision_tree.q4_answered_at = datetime.utcnow()
        else:
            raise ValueError("Invalid question number")
        
        # Determine CCP decision if all questions are answered or if we can stop early
        if not answer or question_number == 4:  # If answer is No or this is Q4
            is_ccp, reasoning = decision_tree.determine_ccp_decision()
            decision_tree.is_ccp = is_ccp
            decision_tree.decision_reasoning = reasoning
            decision_tree.decision_date = datetime.utcnow()
            decision_tree.decision_by = user_id
            decision_tree.status = "completed"
        
        self.db.commit()
        self.db.refresh(decision_tree)
        
        return decision_tree
    
    def get_decision_tree(self, hazard_id: int) -> Optional[DecisionTree]:
        """Get the decision tree for a hazard"""
        return self.db.query(DecisionTree).filter(DecisionTree.hazard_id == hazard_id).first()
    
    def get_decision_tree_status(self, hazard_id: int) -> dict:
        """Get the current status of a decision tree"""
        decision_tree = self.get_decision_tree(hazard_id)
        if not decision_tree:
            return {
                "exists": False,
                "current_question": 1,
                "can_proceed": True,
                "is_ccp": None,
                "status": "not_started"
            }
        
        return {
            "exists": True,
            "current_question": decision_tree.get_current_question(),
            "can_proceed": decision_tree.can_proceed_to_next_question(),
            "is_ccp": decision_tree.is_ccp,
            "status": decision_tree.status,
            "decision_reasoning": decision_tree.decision_reasoning
        }

    # --- HACCP Plan methods ---
    def create_haccp_plan(self, product_id: int, title: str, description: Optional[str], content: str, created_by: int,
                           effective_date: Optional[datetime] = None, review_date: Optional[datetime] = None) -> HACCPPlan:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")

        plan = HACCPPlan(
            product_id=product_id,
            title=title,
            description=description,
            status=HACCPPlanStatus.DRAFT,
            version="1.0",
            current_content=content,
            effective_date=effective_date,
            review_date=review_date,
            created_by=created_by,
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        # Seed initial version
        version = HACCPPlanVersion(
            plan_id=plan.id,
            version_number="1.0",
            content=content,
            change_description="Initial plan",
            created_by=created_by,
        )
        self.db.add(version)
        self.db.commit()

        return plan

    def create_haccp_plan_version(self, plan_id: int, content: str, change_description: Optional[str], change_reason: Optional[str], created_by: int) -> HACCPPlanVersion:
        plan = self.db.query(HACCPPlan).filter(HACCPPlan.id == plan_id).first()
        if not plan:
            raise ValueError("Plan not found")

        # Bump minor version
        import re
        m = re.match(r"^(\d+)\.(\d+)$", plan.version or "1.0")
        if m:
            next_version = f"{int(m.group(1))}.{int(m.group(2)) + 1}"
        else:
            next_version = "1.0"

        version = HACCPPlanVersion(
            plan_id=plan.id,
            version_number=next_version,
            content=content,
            change_description=change_description,
            change_reason=change_reason,
            created_by=created_by,
        )
        self.db.add(version)

        plan.version = next_version
        plan.current_content = content
        plan.status = HACCPPlanStatus.DRAFT
        plan.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(version)
        return version

    def submit_haccp_plan_for_approval(self, plan_id: int, approvals: List[Dict[str, int]], submitted_by: int) -> int:
        plan = self.db.query(HACCPPlan).filter(HACCPPlan.id == plan_id).first()
        if not plan:
            raise ValueError("Plan not found")
        # Clear existing pending approvals
        self.db.query(HACCPPlanApproval).filter(HACCPPlanApproval.plan_id == plan_id, HACCPPlanApproval.status == "pending").delete()
        seen = set()
        count = 0
        for ap in approvals:
            order = int(ap["approval_order"]) if isinstance(ap.get("approval_order"), int) else ap.get("approval_order")
            if order in seen:
                raise ValueError("Duplicate approval_order")
            seen.add(order)
            row = HACCPPlanApproval(plan_id=plan_id, approver_id=ap["approver_id"], approval_order=order, status="pending")
            self.db.add(row)
            count += 1
        plan.status = HACCPPlanStatus.UNDER_REVIEW
        plan.updated_at = datetime.utcnow()
        self.db.commit()
        return count

    def approve_haccp_plan_step(self, plan_id: int, approval_id: int, approver_id: int) -> int:
        step = self.db.query(HACCPPlanApproval).filter(HACCPPlanApproval.id == approval_id, HACCPPlanApproval.plan_id == plan_id).first()
        if not step:
            raise ValueError("Approval step not found")
        if step.approver_id != approver_id:
            raise PermissionError("Not assigned approver")
        if step.status != "pending":
            raise ValueError("Approval step is not pending")
        # Ensure all lower orders are approved
        pending_lower = self.db.query(HACCPPlanApproval).filter(HACCPPlanApproval.plan_id == plan_id, HACCPPlanApproval.approval_order < step.approval_order, HACCPPlanApproval.status != "approved").count()
        if pending_lower > 0:
            raise ValueError("Previous approval steps must be completed first")
        step.status = "approved"
        step.approved_at = datetime.utcnow()
        self.db.commit()
        # If none pending, mark plan approved
        remaining = self.db.query(HACCPPlanApproval).filter(HACCPPlanApproval.plan_id == plan_id, HACCPPlanApproval.status == "pending").count()
        if remaining == 0:
            plan = self.db.query(HACCPPlan).filter(HACCPPlan.id == plan_id).first()
            if plan:
                # Enforce: product must have at least one process flow step before approval
                try:
                    flows_count = self.db.query(ProcessFlow).filter(ProcessFlow.product_id == plan.product_id).count()
                except Exception:
                    flows_count = 0
                if flows_count <= 0:
                    # Revert this step back to approved and keep plan under review
                    plan.status = HACCPPlanStatus.UNDER_REVIEW
                    self.db.commit()
                    raise ValueError("Cannot approve HACCP plan: no process flow steps defined for the product")

                plan.status = HACCPPlanStatus.APPROVED
                plan.approved_by = approver_id
                plan.approved_at = datetime.utcnow()
                self.db.commit()
        return remaining

    def reject_haccp_plan_step(self, plan_id: int, approval_id: int, approver_id: int, comments: Optional[str]) -> None:
        step = self.db.query(HACCPPlanApproval).filter(HACCPPlanApproval.id == approval_id, HACCPPlanApproval.plan_id == plan_id).first()
        if not step:
            raise ValueError("Approval step not found")
        if step.approver_id != approver_id:
            raise PermissionError("Not assigned approver")
        if step.status != "pending":
            raise ValueError("Approval step is not pending")
        step.status = "rejected"
        step.comments = comments
        step.approved_at = datetime.utcnow()
        plan = self.db.query(HACCPPlan).filter(HACCPPlan.id == plan_id).first()
        if plan:
            plan.status = HACCPPlanStatus.DRAFT
        self.db.commit()
        return None
    
    def create_ccp(self, product_id: int, ccp_data: CCPCreate, created_by: int) -> CCP:
        """Create a CCP"""
        
        # Verify product exists
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        ccp = CCP(
            product_id=product_id,
            hazard_id=ccp_data.hazard_id,
            ccp_number=ccp_data.ccp_number,
            ccp_name=ccp_data.ccp_name,
            description=ccp_data.description,
            status=CCPStatus.ACTIVE,
            critical_limit_min=ccp_data.critical_limit_min,
            critical_limit_max=ccp_data.critical_limit_max,
            critical_limit_unit=ccp_data.critical_limit_unit,
            critical_limit_description=ccp_data.critical_limit_description,
            monitoring_frequency=ccp_data.monitoring_frequency,
            monitoring_method=ccp_data.monitoring_method,
            monitoring_responsible=ccp_data.monitoring_responsible,
            monitoring_equipment=ccp_data.monitoring_equipment,
            corrective_actions=ccp_data.corrective_actions,
            verification_frequency=ccp_data.verification_frequency,
            verification_method=ccp_data.verification_method,
            verification_responsible=ccp_data.verification_responsible,
            monitoring_records=ccp_data.monitoring_records,
            verification_records=ccp_data.verification_records,
            created_by=created_by
        )
        
        self.db.add(ccp)
        self.db.commit()
        self.db.refresh(ccp)
        
        return ccp
    
    def create_monitoring_log(self, ccp_id: int, log_data: MonitoringLogCreate, created_by: int) -> Tuple[CCPMonitoringLog, bool]:
        """Create a monitoring log and check for alerts"""
        
        # Verify CCP exists
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        # Competency check removed - any user with HACCP access can log monitoring
        
        # Validate equipment if provided
        if log_data.equipment_id:
            equipment = self.db.query(Equipment).filter(Equipment.id == log_data.equipment_id).first()
            if not equipment:
                raise ValueError("Equipment not found")
            
            # Check if equipment is calibrated
            if not equipment.is_calibrated:
                raise ValueError("Equipment is not calibrated and cannot be used for monitoring")
            
            # Check if equipment is active
            if not equipment.is_active:
                raise ValueError("Equipment is not active and cannot be used for monitoring")
        
        # Check if within limits
        measured_value = log_data.measured_value
        is_within_limits = True
        
        if ccp.critical_limit_min is not None and measured_value < ccp.critical_limit_min:
            is_within_limits = False
        if ccp.critical_limit_max is not None and measured_value > ccp.critical_limit_max:
            is_within_limits = False
        
        # Resolve batch info
        resolved_batch_number = log_data.batch_number
        resolved_batch_id = getattr(log_data, "batch_id", None)
        if resolved_batch_id is not None:
            batch = self.db.query(Batch).filter(Batch.id == resolved_batch_id).first()
            if not batch:
                raise ValueError("Batch not found")
            resolved_batch_number = batch.batch_number

        monitoring_log = CCPMonitoringLog(
            ccp_id=ccp_id,
            batch_id=resolved_batch_id,
            batch_number=resolved_batch_number or "",
            monitoring_time=datetime.utcnow(),
            measured_value=measured_value,
            unit=log_data.unit,
            is_within_limits=is_within_limits,
            additional_parameters=log_data.additional_parameters,
            observations=log_data.observations,
            evidence_files=log_data.evidence_files,
            corrective_action_taken=log_data.corrective_action_taken,
            corrective_action_description=log_data.corrective_action_description,
            corrective_action_by=log_data.corrective_action_by,
            equipment_id=log_data.equipment_id,
            created_by=created_by
        )
        
        self.db.add(monitoring_log)
        self.db.commit()
        self.db.refresh(monitoring_log)
        
        # Update monitoring schedule after successful monitoring
        self.update_schedule_after_monitoring(ccp_id)
        
        # Create alert if out of spec and auto-create Non-Conformance
        alert_created = False
        nc_created = False
        if not is_within_limits:
            alert_created = self._create_out_of_spec_alert(ccp, monitoring_log)
            nc_created = self._create_mandatory_nc_for_out_of_spec(ccp, monitoring_log, created_by)

        return monitoring_log, alert_created, nc_created
    
    def _create_out_of_spec_alert(self, ccp: CCP, monitoring_log: CCPMonitoringLog) -> bool:
        """Create an alert for out-of-spec readings"""
        
        try:
            # Get responsible person
            responsible_user_id = ccp.monitoring_responsible or ccp.created_by
            
            # Create notification
            notification = Notification(
                user_id=responsible_user_id,
                title=f"CCP Out-of-Spec Alert: {ccp.ccp_name}",
                message=f"CCP {ccp.ccp_number} ({ccp.ccp_name}) is out of specification. "
                       f"Batch: {monitoring_log.batch_number}, "
                       f"Value: {monitoring_log.measured_value} {monitoring_log.unit or ''}, "
                       f"Limits: {ccp.critical_limit_min or 'N/A'} - {ccp.critical_limit_max or 'N/A'}",
                notification_type=NotificationType.ERROR,
                priority=NotificationPriority.HIGH,
                category=NotificationCategory.HACCP,
                notification_data={
                    "ccp_id": ccp.id,
                    "ccp_number": ccp.ccp_number,
                    "ccp_name": ccp.ccp_name,
                    "batch_number": monitoring_log.batch_number,
                    "measured_value": monitoring_log.measured_value,
                    "unit": monitoring_log.unit,
                    "critical_limit_min": ccp.critical_limit_min,
                    "critical_limit_max": ccp.critical_limit_max,
                    "monitoring_log_id": monitoring_log.id
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            logger.warning(f"Out-of-spec alert created for CCP {ccp.ccp_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create out-of-spec alert: {str(e)}")
            return False
    
    def get_flowchart_data(self, product_id: int) -> FlowchartData:
        """Generate flowchart data for a product"""
        
        # Get process flows
        process_flows = self.db.query(ProcessFlow).filter(
            ProcessFlow.product_id == product_id
        ).order_by(ProcessFlow.step_number).all()
        
        nodes = []
        edges = []
        
        # Add start node
        nodes.append(FlowchartNode(
            id="start",
            type="start",
            label="Start",
            x=100,
            y=50
        ))
        
        # Add process nodes
        for i, flow in enumerate(process_flows):
            node_id = f"step_{flow.id}"
            x = 100 + (i * 200)
            y = 150
            
            nodes.append(FlowchartNode(
                id=node_id,
                type="process",
                label=flow.step_name,
                x=x,
                y=y,
                data={
                    "step_number": flow.step_number,
                    "description": flow.description,
                    "equipment": flow.equipment,
                    "temperature": flow.temperature,
                    "time_minutes": flow.time_minutes,
                    "ph": flow.ph,
                    "aw": flow.aw,
                    "parameters": flow.parameters
                }
            ))
            
            # Add edge from previous node
            if i == 0:
                edges.append(FlowchartEdge(
                    id=f"edge_start_{node_id}",
                    source="start",
                    target=node_id
                ))
            else:
                prev_node_id = f"step_{process_flows[i-1].id}"
                edges.append(FlowchartEdge(
                    id=f"edge_{prev_node_id}_{node_id}",
                    source=prev_node_id,
                    target=node_id
                ))
        
        # Add end node
        if process_flows:
            last_node_id = f"step_{process_flows[-1].id}"
            nodes.append(FlowchartNode(
                id="end",
                type="end",
                label="End",
                x=100 + (len(process_flows) * 200),
                y=250
            ))
            edges.append(FlowchartEdge(
                id=f"edge_{last_node_id}_end",
                source=last_node_id,
                target="end"
            ))
        
        return FlowchartData(nodes=nodes, edges=edges)
    
    def get_haccp_dashboard_stats(self) -> Dict[str, Any]:
        """Get HACCP dashboard statistics"""
        
        # Get total products
        total_products = self.db.query(Product).count()
        
        # Get approved HACCP plans
        approved_plans = self.db.query(Product).filter(Product.haccp_plan_approved == True).count()
        
        # Get total CCPs
        total_ccps = self.db.query(CCP).count()
        
        # Get active CCPs
        active_ccps = self.db.query(CCP).filter(CCP.status == CCPStatus.ACTIVE).count()
        
        # Get recent monitoring logs
        recent_logs = self.db.query(CCPMonitoringLog).order_by(
            desc(CCPMonitoringLog.monitoring_time)
        ).limit(5).all()
        
        # Get out-of-spec incidents
        out_of_spec_count = self.db.query(CCPMonitoringLog).filter(
            CCPMonitoringLog.is_within_limits == False
        ).count()
        
        # Get recent alerts
        recent_alerts = self.db.query(CCPMonitoringLog).filter(
            and_(
                CCPMonitoringLog.is_within_limits == False,
                CCPMonitoringLog.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        ).count()
        
        return {
            "total_products": total_products,
            "approved_plans": approved_plans,
            "total_ccps": total_ccps,
            "active_ccps": active_ccps,
            "out_of_spec_count": out_of_spec_count,
            "recent_alerts": recent_alerts,
            "recent_logs": [
                {
                    "id": log.id,
                    "ccp_name": log.ccp.ccp_name,
                    "batch_number": log.batch_number,
                    "measured_value": log.measured_value,
                    "unit": log.unit,
                    "is_within_limits": log.is_within_limits,
                    "monitoring_time": log.monitoring_time.isoformat() if log.monitoring_time else None,
                } for log in recent_logs
            ]
        }
    
    def generate_haccp_report(self, product_id: int, report_type: str, 
                            date_from: Optional[datetime] = None,
                            date_to: Optional[datetime] = None) -> Dict[str, Any]:
        """Generate HACCP report data"""
        
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError("Product not found")
        
        # Get process flows
        process_flows = self.db.query(ProcessFlow).filter(
            ProcessFlow.product_id == product_id
        ).order_by(ProcessFlow.step_number).all()
        
        # Get hazards
        hazards = self.db.query(Hazard).filter(
            Hazard.product_id == product_id
        ).all()
        
        # Get CCPs
        ccps = self.db.query(CCP).filter(
            CCP.product_id == product_id
        ).all()
        
        # Get monitoring logs if date range specified
        monitoring_logs = []
        if date_from and date_to:
            monitoring_logs = self.db.query(CCPMonitoringLog).filter(
                and_(
                    CCPMonitoringLog.ccp_id.in_([ccp.id for ccp in ccps]),
                    CCPMonitoringLog.monitoring_time >= date_from,
                    CCPMonitoringLog.monitoring_time <= date_to
                )
            ).order_by(desc(CCPMonitoringLog.monitoring_time)).all()
        
        report_data = {
            "product": {
                "id": product.id,
                "product_code": product.product_code,
                "name": product.name,
                "category": product.category,
                "haccp_plan_approved": product.haccp_plan_approved,
                "haccp_plan_version": product.haccp_plan_version,
            },
            "process_flows": [
                {
                    "step_number": flow.step_number,
                    "step_name": flow.step_name,
                    "description": flow.description,
                    "equipment": flow.equipment,
                    "temperature": flow.temperature,
                    "time_minutes": flow.time_minutes,
                    "ph": flow.ph,
                    "aw": flow.aw,
                } for flow in process_flows
            ],
            "hazards": [
                {
                    "hazard_name": hazard.hazard_name,
                    "hazard_type": hazard.hazard_type.value,
                    "risk_score": hazard.risk_score,
                    "risk_level": hazard.risk_level.value,
                    "is_ccp": hazard.is_ccp,
                } for hazard in hazards
            ],
            "ccps": [
                {
                    "ccp_number": ccp.ccp_number,
                    "ccp_name": ccp.ccp_name,
                    "critical_limit_min": ccp.critical_limit_min,
                    "critical_limit_max": ccp.critical_limit_max,
                    "critical_limit_unit": ccp.critical_limit_unit,
                    "monitoring_frequency": ccp.monitoring_frequency,
                    "corrective_actions": ccp.corrective_actions,
                } for ccp in ccps
            ],
            "monitoring_summary": {
                "total_logs": len(monitoring_logs),
                "in_spec_count": len([log for log in monitoring_logs if log.is_within_limits]),
                "out_of_spec_count": len([log for log in monitoring_logs if not log.is_within_limits]),
            },
            "generated_at": datetime.utcnow().isoformat(),
            "report_type": report_type,
            "date_range": {
                "from": date_from.isoformat() if date_from else None,
                "to": date_to.isoformat() if date_to else None,
            }
        }
        
        return report_data 

    def add_validation_evidence(self, ccp_id: int, evidence_data: dict, user_id: int) -> CCP:
        """Add validation evidence to a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        # Get existing validation evidence or initialize empty list
        current_evidence = ccp.validation_evidence or []
        
        # Add new evidence with metadata
        new_evidence = {
            **evidence_data,
            "added_by": user_id,
            "added_at": datetime.utcnow().isoformat(),
            "evidence_id": len(current_evidence) + 1
        }
        
        current_evidence.append(new_evidence)
        ccp.validation_evidence = current_evidence
        ccp.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ccp)
        
        return ccp
    
    def remove_validation_evidence(self, ccp_id: int, evidence_id: int, user_id: int) -> CCP:
        """Remove validation evidence from a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        current_evidence = ccp.validation_evidence or []
        
        # Find and remove the evidence
        updated_evidence = [e for e in current_evidence if e.get("evidence_id") != evidence_id]
        
        if len(updated_evidence) == len(current_evidence):
            raise ValueError("Evidence not found")
        
        ccp.validation_evidence = updated_evidence
        ccp.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ccp)
        
        return ccp
    
    def get_validation_evidence_summary(self, ccp_id: int) -> dict:
        """Get a summary of validation evidence for a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        evidence = ccp.validation_evidence or []
        
        # Group evidence by type
        evidence_by_type = {}
        for e in evidence:
            evidence_type = e.get("type", "unknown")
            if evidence_type not in evidence_by_type:
                evidence_by_type[evidence_type] = []
            evidence_by_type[evidence_type].append(e)
        
        return {
            "total_evidence": len(evidence),
            "evidence_by_type": evidence_by_type,
            "has_sop_references": any(e.get("type") == "sop_reference" for e in evidence),
            "has_scientific_studies": any(e.get("type") == "scientific_study" for e in evidence),
            "has_process_authority": any(e.get("type") == "process_authority_letter" for e in evidence),
            "validation_complete": len(evidence) > 0
        } 
    def add_validation_evidence(self, ccp_id: int, evidence_data: dict, user_id: int) -> CCP:
        """Add validation evidence to a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        # Get existing validation evidence or initialize empty list
        current_evidence = ccp.validation_evidence or []
        
        # Add new evidence with metadata
        new_evidence = {
            **evidence_data,
            "added_by": user_id,
            "added_at": datetime.utcnow().isoformat(),
            "evidence_id": len(current_evidence) + 1
        }
        
        current_evidence.append(new_evidence)
        ccp.validation_evidence = current_evidence
        ccp.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ccp)
        
        return ccp
    
    def remove_validation_evidence(self, ccp_id: int, evidence_id: int, user_id: int) -> CCP:
        """Remove validation evidence from a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        current_evidence = ccp.validation_evidence or []
        
        # Find and remove the evidence
        updated_evidence = [e for e in current_evidence if e.get("evidence_id") != evidence_id]
        
        if len(updated_evidence) == len(current_evidence):
            raise ValueError("Evidence not found")
        
        ccp.validation_evidence = updated_evidence
        ccp.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ccp)
        
        return ccp
    
    def get_validation_evidence_summary(self, ccp_id: int) -> dict:
        """Get a summary of validation evidence for a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        evidence = ccp.validation_evidence or []
        
        # Group evidence by type
        evidence_by_type = {}
        for e in evidence:
            evidence_type = e.get("type", "unknown")
            if evidence_type not in evidence_by_type:
                evidence_by_type[evidence_type] = []
            evidence_by_type[evidence_type].append(e)
        
        return {
            "total_evidence": len(evidence),
            "evidence_by_type": evidence_by_type,
            "has_sop_references": any(e.get("type") == "sop_reference" for e in evidence),
            "has_scientific_studies": any(e.get("type") == "scientific_study" for e in evidence),
            "has_process_authority": any(e.get("type") == "process_authority_letter" for e in evidence),
            "validation_complete": len(evidence) > 0
        }

    def create_monitoring_schedule(self, schedule_data: dict, created_by: int) -> CCPMonitoringSchedule:
        """Create a monitoring schedule for a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == schedule_data["ccp_id"]).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        # Check if schedule already exists
        existing_schedule = self.db.query(CCPMonitoringSchedule).filter(
            CCPMonitoringSchedule.ccp_id == schedule_data["ccp_id"]
        ).first()
        
        if existing_schedule:
            raise ValueError("Monitoring schedule already exists for this CCP")
        
        # Validate schedule configuration
        if schedule_data["schedule_type"] == "interval" and not schedule_data.get("interval_minutes"):
            raise ValueError("Interval minutes required for interval-based schedules")
        
        if schedule_data["schedule_type"] == "cron" and not schedule_data.get("cron_expression"):
            raise ValueError("Cron expression required for cron-based schedules")
        
        # Create schedule
        schedule = CCPMonitoringSchedule(
            ccp_id=schedule_data["ccp_id"],
            schedule_type=schedule_data["schedule_type"],
            interval_minutes=schedule_data.get("interval_minutes"),
            cron_expression=schedule_data.get("cron_expression"),
            tolerance_window_minutes=schedule_data.get("tolerance_window_minutes", 15),
            is_active=schedule_data.get("is_active", True),
            created_by=created_by
        )
        
        # Calculate initial next due time
        schedule.next_due_time = schedule.calculate_next_due()
        
        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)
        
        return schedule
    
    def update_monitoring_schedule(self, schedule_id: int, update_data: dict, updated_by: int) -> CCPMonitoringSchedule:
        """Update a monitoring schedule"""
        schedule = self.db.query(CCPMonitoringSchedule).filter(CCPMonitoringSchedule.id == schedule_id).first()
        if not schedule:
            raise ValueError("Monitoring schedule not found")
        
        # Validate schedule configuration
        if update_data.get("schedule_type") == "interval" and not update_data.get("interval_minutes"):
            raise ValueError("Interval minutes required for interval-based schedules")
        
        if update_data.get("schedule_type") == "cron" and not update_data.get("cron_expression"):
            raise ValueError("Cron expression required for cron-based schedules")
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(schedule, field):
                setattr(schedule, field, value)
        
        # Recalculate next due time if schedule type or timing changed
        if any(field in update_data for field in ["schedule_type", "interval_minutes", "cron_expression"]):
            schedule.next_due_time = schedule.calculate_next_due()
        
        schedule.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(schedule)
        
        return schedule
    
    def get_monitoring_schedule_status(self, ccp_id: int) -> Optional[MonitoringScheduleStatus]:
        """Get monitoring schedule status for a CCP"""
        schedule = self.db.query(CCPMonitoringSchedule).filter(
            CCPMonitoringSchedule.ccp_id == ccp_id,
            CCPMonitoringSchedule.is_active == True
        ).first()
        
        if not schedule:
            return None
        
        # Get last monitoring time
        last_monitoring = self.db.query(CCPMonitoringLog).filter(
            CCPMonitoringLog.ccp_id == ccp_id
        ).order_by(desc(CCPMonitoringLog.monitoring_time)).first()
        
        last_monitoring_time = last_monitoring.monitoring_time if last_monitoring else None
        
        return MonitoringScheduleStatus(
            schedule_id=schedule.id,
            ccp_id=schedule.ccp_id,
            ccp_name=schedule.ccp.ccp_name,
            is_due=schedule.is_due(),
            is_overdue=schedule.is_overdue(),
            next_due_time=schedule.next_due_time,
            last_monitoring_time=last_monitoring_time,
            tolerance_window_minutes=schedule.tolerance_window_minutes,
            schedule_type=schedule.schedule_type,
            is_active=schedule.is_active
        )
    
    def get_all_due_monitoring(self) -> List[MonitoringScheduleStatus]:
        """Get all CCPs that are due for monitoring"""
        schedules = self.db.query(CCPMonitoringSchedule).filter(
            CCPMonitoringSchedule.is_active == True
        ).all()
        
        due_schedules = []
        current_time = datetime.utcnow()
        
        for schedule in schedules:
            if schedule.is_due(current_time) or schedule.is_overdue(current_time):
                # Get last monitoring time
                last_monitoring = self.db.query(CCPMonitoringLog).filter(
                    CCPMonitoringLog.ccp_id == schedule.ccp_id
                ).order_by(desc(CCPMonitoringLog.monitoring_time)).first()
                
                last_monitoring_time = last_monitoring.monitoring_time if last_monitoring else None
                
                due_schedules.append(MonitoringScheduleStatus(
                    schedule_id=schedule.id,
                    ccp_id=schedule.ccp_id,
                    ccp_name=schedule.ccp.ccp_name,
                    is_due=schedule.is_due(current_time),
                    is_overdue=schedule.is_overdue(current_time),
                    next_due_time=schedule.next_due_time,
                    last_monitoring_time=last_monitoring_time,
                    tolerance_window_minutes=schedule.tolerance_window_minutes,
                    schedule_type=schedule.schedule_type,
                    is_active=schedule.is_active
                ))
        
        return due_schedules
    
    def update_schedule_after_monitoring(self, ccp_id: int) -> None:
        """Update schedule after monitoring is completed"""
        schedule = self.db.query(CCPMonitoringSchedule).filter(
            CCPMonitoringSchedule.ccp_id == ccp_id,
            CCPMonitoringSchedule.is_active == True
        ).first()
        
        if schedule:
            schedule.last_scheduled_time = datetime.utcnow()
            schedule.next_due_time = schedule.calculate_next_due()
            self.db.commit()

    def _create_mandatory_nc_for_out_of_spec(self, ccp: CCP, monitoring_log: CCPMonitoringLog, created_by: int) -> bool:
        """Create a mandatory Non-Conformance for out-of-spec monitoring"""
        
        try:
            from app.schemas.nonconformance import (
                NonConformanceCreate as NCCreate,
                NonConformanceSource,
            )
            from app.services.nonconformance_service import NonConformanceService
            from app.models.traceability import Batch, BatchStatus

            # Determine severity heuristically
            severity = "high"
            try:
                if ccp.critical_limit_max is not None and monitoring_log.measured_value is not None:
                    # If exceeds by >10% of max range, mark critical
                    range_span = (
                        (ccp.critical_limit_max - (ccp.critical_limit_min or 0))
                        if ccp.critical_limit_min is not None
                        else ccp.critical_limit_max or 1
                    )
                    if range_span:
                        delta = abs(monitoring_log.measured_value - (ccp.critical_limit_max or 0))
                        if delta > 0.1 * abs(range_span):
                            severity = "critical"
            except Exception:
                pass

            nc_title = f"CCP Out-of-Spec: {ccp.ccp_name}"
            nc_description = (
                f"Batch {monitoring_log.batch_number}: {monitoring_log.measured_value}"
                f"{(' ' + (monitoring_log.unit or '')) if monitoring_log.unit else ''} outside limits"
                f" ({ccp.critical_limit_min or 'N/A'} - {ccp.critical_limit_max or 'N/A'})."
                f"\n\nMonitoring Log ID: {monitoring_log.id}"
                f"\nCCP: {ccp.ccp_number} - {ccp.ccp_name}"
                f"\nProduct: {ccp.product_id}"
            )
            process_ref = f"Product:{ccp.product_id}/CCP:{ccp.id}"

            nc_data = NCCreate(
                title=nc_title,
                description=nc_description,
                source=NonConformanceSource.HACCP,
                batch_reference=monitoring_log.batch_number,
                product_reference=str(ccp.product_id),
                process_reference=process_ref,
                location=None,
                severity=severity,
                impact_area="food_safety",
                category="CCP_Out_of_Spec",
                target_resolution_date=datetime.utcnow() + timedelta(days=7),
            )

            nc_service = NonConformanceService(self.db)
            reporter = created_by
            nc = nc_service.create_non_conformance(nc_data, reporter)
            
            # Automatically quarantine the affected batch
            if monitoring_log.batch_id:
                self._quarantine_batch_for_out_of_spec(monitoring_log.batch_id, ccp, monitoring_log, nc.id)
            
            logger.warning(f"Mandatory NC created for out-of-spec CCP {ccp.ccp_number}: NC ID {nc.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create mandatory NC for out-of-spec: {str(e)}")
            # Don't fail the monitoring log creation, but log the error
            return False
    
    def _quarantine_batch_for_out_of_spec(self, batch_id: int, ccp: CCP, monitoring_log: CCPMonitoringLog, nc_id: int) -> bool:
        """Automatically quarantine a batch due to out-of-spec CCP monitoring"""
        
        try:
            from app.models.traceability import Batch, BatchStatus
            
            batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                logger.warning(f"Batch {batch_id} not found for quarantine")
                return False
            
            # Only quarantine if not already quarantined
            if batch.status != BatchStatus.QUARANTINED:
                batch.status = BatchStatus.QUARANTINED
                
                # Add quarantine metadata
                if not batch.test_results:
                    batch.test_results = {}
                
                batch.test_results["quarantine_info"] = {
                    "quarantined_at": datetime.utcnow().isoformat(),
                    "quarantine_reason": "CCP_Out_of_Spec",
                    "ccp_id": ccp.id,
                    "ccp_name": ccp.ccp_name,
                    "monitoring_log_id": monitoring_log.id,
                    "nc_id": nc_id,
                    "measured_value": monitoring_log.measured_value,
                    "unit": monitoring_log.unit,
                    "critical_limit_min": ccp.critical_limit_min,
                    "critical_limit_max": ccp.critical_limit_max
                }
                
                self.db.commit()
                logger.warning(f"Batch {batch.batch_number} quarantined due to out-of-spec CCP {ccp.ccp_number}")
                return True
            else:
                logger.info(f"Batch {batch.batch_number} already quarantined")
                return True
                
        except Exception as e:
            logger.error(f"Failed to quarantine batch {batch_id}: {str(e)}")
            return False

    def release_batch_from_quarantine(self, batch_id: int, disposition_data: dict, approved_by: int) -> bool:
        """Release a batch from quarantine with QA disposition approval"""
        
        try:
            from app.models.traceability import Batch, BatchStatus
            from app.models.user import User
            
            batch = self.db.query(Batch).filter(Batch.id == batch_id).first()
            if not batch:
                raise ValueError("Batch not found")
            
            if batch.status != BatchStatus.QUARANTINED:
                raise ValueError("Batch is not quarantined")
            
            # Validate disposition data
            disposition_type = disposition_data.get("disposition_type")
            if disposition_type not in ["release", "dispose", "rework"]:
                raise ValueError("Invalid disposition type")
            
            disposition_reason = disposition_data.get("disposition_reason")
            if not disposition_reason:
                raise ValueError("Disposition reason is required")
            
            # Get approver details
            approver = self.db.query(User).filter(User.id == approved_by).first()
            if not approver:
                raise ValueError("Approver not found")
            
            # Update batch status based on disposition
            if disposition_type == "release":
                batch.status = BatchStatus.RELEASED
            elif disposition_type == "dispose":
                batch.status = BatchStatus.DISPOSED
            elif disposition_type == "rework":
                batch.status = BatchStatus.IN_PRODUCTION  # Back to production for rework
            
            # Add disposition metadata
            if not batch.test_results:
                batch.test_results = {}
            
            batch.test_results["disposition_info"] = {
                "disposition_type": disposition_type,
                "disposition_reason": disposition_reason,
                "disposition_date": datetime.utcnow().isoformat(),
                "approved_by": approved_by,
                "approver_name": approver.full_name,
                "approver_role": approver.role.name if approver.role else "Unknown",
                "additional_notes": disposition_data.get("additional_notes", ""),
                "corrective_actions_taken": disposition_data.get("corrective_actions_taken", ""),
                "verification_tests": disposition_data.get("verification_tests", [])
            }
            
            # If releasing, add release metadata
            if disposition_type == "release":
                batch.test_results["release_info"] = {
                    "released_at": datetime.utcnow().isoformat(),
                    "released_by": approved_by,
                    "release_conditions": disposition_data.get("release_conditions", ""),
                    "quality_checks_passed": disposition_data.get("quality_checks_passed", True)
                }
            
            self.db.commit()
            
            logger.info(f"Batch {batch.batch_number} {disposition_type}d by {approver.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to release batch {batch_id} from quarantine: {str(e)}")
            raise
    
    def get_quarantined_batches(self) -> List[dict]:
        """Get all quarantined batches with their quarantine information"""
        
        try:
            from app.models.traceability import Batch, BatchStatus
            
            quarantined_batches = self.db.query(Batch).filter(
                Batch.status == BatchStatus.QUARANTINED
            ).all()
            
            result = []
            for batch in quarantined_batches:
                quarantine_info = batch.test_results.get("quarantine_info", {}) if batch.test_results else {}
                
                result.append({
                    "batch_id": batch.id,
                    "batch_number": batch.batch_number,
                    "product_name": batch.product_name,
                    "quarantined_at": quarantine_info.get("quarantined_at"),
                    "quarantine_reason": quarantine_info.get("quarantine_reason"),
                    "ccp_name": quarantine_info.get("ccp_name"),
                    "measured_value": quarantine_info.get("measured_value"),
                    "unit": quarantine_info.get("unit"),
                    "critical_limit_min": quarantine_info.get("critical_limit_min"),
                    "critical_limit_max": quarantine_info.get("critical_limit_max"),
                    "nc_id": quarantine_info.get("nc_id"),
                    "monitoring_log_id": quarantine_info.get("monitoring_log_id")
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get quarantined batches: {str(e)}")
            return []

    def create_verification_program(self, program_data: dict, created_by: int) -> CCPVerificationProgram:
        """Create a verification program for a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == program_data["ccp_id"]).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        # Validate frequency configuration
        if program_data["frequency"] == "custom" and not program_data.get("frequency_value"):
            raise ValueError("Frequency value required for custom frequency")
        
        # Create verification program
        program = CCPVerificationProgram(
            ccp_id=program_data["ccp_id"],
            verification_type=program_data["verification_type"],
            frequency=program_data["frequency"],
            frequency_value=program_data.get("frequency_value"),
            required_verifier_role=program_data.get("required_verifier_role"),
            verification_criteria=program_data.get("verification_criteria"),
            sampling_plan=program_data.get("sampling_plan"),
            is_active=program_data.get("is_active", True),
            created_by=created_by
        )
        
        # Calculate initial next verification date
        program.next_verification_date = program.calculate_next_verification_date()
        
        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)
        
        return program
    
    def get_verification_programs_for_ccp(self, ccp_id: int) -> List[CCPVerificationProgram]:
        """Get all verification programs for a CCP"""
        return self.db.query(CCPVerificationProgram).filter(
            CCPVerificationProgram.ccp_id == ccp_id,
            CCPVerificationProgram.is_active == True
        ).all()
    
    def get_due_verifications(self) -> List[dict]:
        """Get all verification programs that are due"""
        programs = self.db.query(CCPVerificationProgram).filter(
            CCPVerificationProgram.is_active == True
        ).all()
        
        due_programs = []
        current_time = datetime.utcnow()
        
        for program in programs:
            if program.is_due(current_time) or program.is_overdue(current_time):
                due_programs.append({
                    "program_id": program.id,
                    "ccp_id": program.ccp_id,
                    "ccp_name": program.ccp.ccp_name,
                    "verification_type": program.verification_type,
                    "frequency": program.frequency,
                    "next_verification_date": program.next_verification_date,
                    "is_overdue": program.is_overdue(current_time),
                    "required_verifier_role": program.required_verifier_role,
                    "verification_criteria": program.verification_criteria
                })
        
        return due_programs
    
    def create_verification_log_with_role_check(self, ccp_id: int, log_data: dict, created_by: int) -> CCPVerificationLog:
        """Create a verification log with role segregation enforcement"""
        
        # Get the CCP and its verification programs
        ccp = self.db.query(CCP).filter(CCP.id == ccp_id).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        # Check if user is trying to verify their own monitoring logs
        if ccp.monitoring_responsible == created_by:
            raise ValueError("User cannot verify their own monitoring logs. Role segregation is required.")
        
        # Check if user has required role for verification
        verification_program_id = log_data.get("verification_program_id")
        if verification_program_id:
            program = self.db.query(CCPVerificationProgram).filter(
                CCPVerificationProgram.id == verification_program_id
            ).first()
            
            if program and program.required_verifier_role:
                # Get user's role
                user = self.db.query(User).filter(User.id == created_by).first()
                if not user or not user.role or user.role.name != program.required_verifier_role:
                    raise ValueError(f"User must have role '{program.required_verifier_role}' to perform this verification")
        
        # Create verification log
        verification_log = CCPVerificationLog(
            ccp_id=ccp_id,
            verification_program_id=verification_program_id,
            verification_date=datetime.utcnow(),
            verification_method=log_data.get("verification_method"),
            verification_result=log_data.get("verification_result"),
            is_compliant=log_data.get("is_compliant", True),
            samples_tested=log_data.get("samples_tested"),
            test_results=log_data.get("test_results"),
            equipment_calibration=log_data.get("equipment_calibration"),
            calibration_date=log_data.get("calibration_date"),
            verifier_role=log_data.get("verifier_role"),
            verification_notes=log_data.get("verification_notes"),
            evidence_files=log_data.get("evidence_files"),
            created_by=created_by
        )
        
        self.db.add(verification_log)
        self.db.commit()
        self.db.refresh(verification_log)
        
        # Update verification program schedule
        if verification_program_id:
            program = self.db.query(CCPVerificationProgram).filter(
                CCPVerificationProgram.id == verification_program_id
            ).first()
            if program:
                program.last_verification_date = datetime.utcnow()
                program.next_verification_date = program.calculate_next_verification_date()
                self.db.commit()
        
        return verification_log
    
    def create_validation(self, validation_data: dict, created_by: int) -> CCPValidation:
        """Create a validation for a CCP"""
        ccp = self.db.query(CCP).filter(CCP.id == validation_data["ccp_id"]).first()
        if not ccp:
            raise ValueError("CCP not found")
        
        # Create validation
        validation = CCPValidation(
            ccp_id=validation_data["ccp_id"],
            validation_type=validation_data["validation_type"],
            validation_title=validation_data["validation_title"],
            validation_description=validation_data.get("validation_description"),
            document_id=validation_data.get("document_id"),
            external_reference=validation_data.get("external_reference"),
            validation_date=validation_data.get("validation_date"),
            valid_until=validation_data.get("valid_until"),
            validation_result=validation_data.get("validation_result"),
            critical_limits_validated=validation_data.get("critical_limits_validated"),
            is_active=validation_data.get("is_active", True),
            created_by=created_by
        )
        
        self.db.add(validation)
        self.db.commit()
        self.db.refresh(validation)
        
        return validation
    
    def review_validation(self, validation_id: int, review_data: dict, reviewed_by: int) -> CCPValidation:
        """Review a validation (approve/reject)"""
        validation = self.db.query(CCPValidation).filter(CCPValidation.id == validation_id).first()
        if not validation:
            raise ValueError("Validation not found")
        
        validation.review_status = review_data["review_status"]
        validation.review_notes = review_data.get("review_notes")
        validation.reviewed_by = reviewed_by
        validation.reviewed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(validation)
        
        return validation
    
    def get_validations_for_ccp(self, ccp_id: int) -> List[CCPValidation]:
        """Get all validations for a CCP"""
        return self.db.query(CCPValidation).filter(
            CCPValidation.ccp_id == ccp_id,
            CCPValidation.is_active == True
        ).all()
    
    def check_ccp_validation_status(self, ccp_id: int) -> dict:
        """Check if a CCP has sufficient validation for approval"""
        validations = self.get_validations_for_ccp(ccp_id)
        
        # Count valid validations by type
        valid_validations = [v for v in validations if v.is_valid_for_approval()]
        
        validation_summary = {
            "total_validations": len(validations),
            "valid_validations": len(valid_validations),
            "expired_validations": len([v for v in validations if v.is_expired()]),
            "pending_reviews": len([v for v in validations if v.review_status == "pending"]),
            "validation_types": {},
            "can_approve": len(valid_validations) > 0
        }
        
        for validation in valid_validations:
            if validation.validation_type not in validation_summary["validation_types"]:
                validation_summary["validation_types"][validation.validation_type] = 0
            validation_summary["validation_types"][validation.validation_type] += 1
        
        return validation_summary

    def create_evidence_attachment(self, attachment_data: dict, uploaded_by: int) -> HACCPEvidenceAttachment:
        """Create an evidence attachment linked to a HACCP record"""
        
        # Validate that the record exists
        record_type = attachment_data["record_type"]
        record_id = attachment_data["record_id"]
        
        if record_type == "monitoring_log":
            record = self.db.query(CCPMonitoringLog).filter(CCPMonitoringLog.id == record_id).first()
        elif record_type == "verification_log":
            record = self.db.query(CCPVerificationLog).filter(CCPVerificationLog.id == record_id).first()
        elif record_type == "validation":
            record = self.db.query(CCPValidation).filter(CCPValidation.id == record_id).first()
        elif record_type == "ccp":
            record = self.db.query(CCP).filter(CCP.id == record_id).first()
        elif record_type == "hazard":
            record = self.db.query(Hazard).filter(Hazard.id == record_id).first()
        else:
            raise ValueError(f"Invalid record_type: {record_type}")
        
        if not record:
            raise ValueError(f"{record_type} with id {record_id} not found")
        
        # Validate that the document exists
        document = self.db.query(Document).filter(Document.id == attachment_data["document_id"]).first()
        if not document:
            raise ValueError("Document not found")
        
        # Create evidence attachment
        attachment = HACCPEvidenceAttachment(
            record_type=attachment_data["record_type"],
            record_id=attachment_data["record_id"],
            document_id=attachment_data["document_id"],
            evidence_type=attachment_data["evidence_type"],
            description=attachment_data.get("description"),
            uploaded_by=uploaded_by,
            file_size=attachment_data.get("file_size"),
            file_type=attachment_data.get("file_type")
        )
        
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        
        # Log the evidence attachment creation
        self._log_audit_event(
            event_type="create",
            event_description=f"Evidence attachment created for {record_type} {record_id}",
            record_type=record_type,
            record_id=record_id,
            user_id=uploaded_by,
            new_values=f"Document: {document.title}, Type: {attachment_data['evidence_type']}"
        )
        
        return attachment
    
    def get_evidence_attachments(self, record_type: str, record_id: int) -> List[HACCPEvidenceAttachment]:
        """Get all evidence attachments for a specific record"""
        return self.db.query(HACCPEvidenceAttachment).filter(
            HACCPEvidenceAttachment.record_type == record_type,
            HACCPEvidenceAttachment.record_id == record_id
        ).all()
    
    def delete_evidence_attachment(self, attachment_id: int, deleted_by: int) -> bool:
        """Delete an evidence attachment"""
        attachment = self.db.query(HACCPEvidenceAttachment).filter(
            HACCPEvidenceAttachment.id == attachment_id
        ).first()
        
        if not attachment:
            raise ValueError("Evidence attachment not found")
        
        # Log the deletion before removing
        self._log_audit_event(
            event_type="delete",
            event_description=f"Evidence attachment deleted",
            record_type=attachment.record_type,
            record_id=attachment.record_id,
            user_id=deleted_by,
            old_values=f"Document ID: {attachment.document_id}, Type: {attachment.evidence_type}"
        )
        
        self.db.delete(attachment)
        self.db.commit()
        
        return True
    
    def _log_audit_event(self, event_type: str, event_description: str, record_type: str, 
                        record_id: int, user_id: int, old_values: str = None, 
                        new_values: str = None, changed_fields: str = None,
                        signature_hash: str = None, signature_method: str = None,
                        ip_address: str = None, user_agent: str = None, 
                        session_id: str = None) -> HACCPAuditLog:
        """Log an audit event for HACCP activities"""
        
        # Get user role
        user = self.db.query(User).filter(User.id == user_id).first()
        user_role = user.role.name if user and user.role else None
        
        # Create audit log entry
        audit_log = HACCPAuditLog(
            event_type=event_type,
            event_description=event_description,
            record_type=record_type,
            record_id=record_id,
            user_id=user_id,
            user_role=user_role,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            signature_hash=signature_hash,
            signature_timestamp=datetime.utcnow() if signature_hash else None,
            signature_method=signature_method,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_audit_logs(self, record_type: str = None, record_id: int = None, 
                      event_type: str = None, user_id: int = None,
                      start_date: datetime = None, end_date: datetime = None,
                      skip: int = 0, limit: int = 100) -> dict:
        """Get audit logs with filtering and pagination"""
        
        query = self.db.query(HACCPAuditLog)
        
        # Apply filters
        if record_type:
            query = query.filter(HACCPAuditLog.record_type == record_type)
        if record_id:
            query = query.filter(HACCPAuditLog.record_id == record_id)
        if event_type:
            query = query.filter(HACCPAuditLog.event_type == event_type)
        if user_id:
            query = query.filter(HACCPAuditLog.user_id == user_id)
        if start_date:
            query = query.filter(HACCPAuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(HACCPAuditLog.created_at <= end_date)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        logs = query.order_by(HACCPAuditLog.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "items": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    def add_e_signature(self, record_type: str, record_id: int, user_id: int,
                       signature_hash: str, signature_method: str = "digital_signature",
                       ip_address: str = None, user_agent: str = None,
                       session_id: str = None) -> HACCPAuditLog:
        """Add an e-signature to a HACCP record"""
        
        # Validate that the record exists
        if record_type == "monitoring_log":
            record = self.db.query(CCPMonitoringLog).filter(CCPMonitoringLog.id == record_id).first()
        elif record_type == "verification_log":
            record = self.db.query(CCPVerificationLog).filter(CCPVerificationLog.id == record_id).first()
        elif record_type == "validation":
            record = self.db.query(CCPValidation).filter(CCPValidation.id == record_id).first()
        elif record_type == "ccp":
            record = self.db.query(CCP).filter(CCP.id == record_id).first()
        elif record_type == "hazard":
            record = self.db.query(Hazard).filter(Hazard.id == record_id).first()
        else:
            raise ValueError(f"Invalid record_type: {record_type}")
        
        if not record:
            raise ValueError(f"{record_type} with id {record_id} not found")
        
        # Log the e-signature
        audit_log = self._log_audit_event(
            event_type="e_signature",
            event_description=f"E-signature added to {record_type} {record_id}",
            record_type=record_type,
            record_id=record_id,
            user_id=user_id,
            signature_hash=signature_hash,
            signature_method=signature_method,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        return audit_log

    def create_evidence_attachment(self, attachment_data: dict, uploaded_by: int) -> HACCPEvidenceAttachment:
        """Create an evidence attachment linked to a HACCP record"""
        
        # Validate that the record exists
        record_type = attachment_data["record_type"]
        record_id = attachment_data["record_id"]
        
        if record_type == "monitoring_log":
            record = self.db.query(CCPMonitoringLog).filter(CCPMonitoringLog.id == record_id).first()
        elif record_type == "verification_log":
            record = self.db.query(CCPVerificationLog).filter(CCPVerificationLog.id == record_id).first()
        elif record_type == "validation":
            record = self.db.query(CCPValidation).filter(CCPValidation.id == record_id).first()
        elif record_type == "ccp":
            record = self.db.query(CCP).filter(CCP.id == record_id).first()
        elif record_type == "hazard":
            record = self.db.query(Hazard).filter(Hazard.id == record_id).first()
        else:
            raise ValueError(f"Invalid record_type: {record_type}")
        
        if not record:
            raise ValueError(f"{record_type} with id {record_id} not found")
        
        # Validate that the document exists
        document = self.db.query(Document).filter(Document.id == attachment_data["document_id"]).first()
        if not document:
            raise ValueError("Document not found")
        
        # Create evidence attachment
        attachment = HACCPEvidenceAttachment(
            record_type=attachment_data["record_type"],
            record_id=attachment_data["record_id"],
            document_id=attachment_data["document_id"],
            evidence_type=attachment_data["evidence_type"],
            description=attachment_data.get("description"),
            uploaded_by=uploaded_by,
            file_size=attachment_data.get("file_size"),
            file_type=attachment_data.get("file_type")
        )
        
        self.db.add(attachment)
        self.db.commit()
        self.db.refresh(attachment)
        
        return attachment

    def _log_audit_event(self, event_type: str, event_description: str, record_type: str, 
                        record_id: int, user_id: int, old_values: str = None, 
                        new_values: str = None, changed_fields: str = None,
                        signature_hash: str = None, signature_method: str = None,
                        ip_address: str = None, user_agent: str = None, 
                        session_id: str = None) -> HACCPAuditLog:
        """Log an audit event for HACCP activities"""
        
        # Get user role
        user = self.db.query(User).filter(User.id == user_id).first()
        user_role = user.role.name if user and user.role else None
        
        # Create audit log entry
        audit_log = HACCPAuditLog(
            event_type=event_type,
            event_description=event_description,
            record_type=record_type,
            record_id=record_id,
            user_id=user_id,
            user_role=user_role,
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields,
            signature_hash=signature_hash,
            signature_timestamp=datetime.utcnow() if signature_hash else None,
            signature_method=signature_method,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
