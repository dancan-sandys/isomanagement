import os
import json
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import uuid

from app.models.haccp import (
    Product, ProcessFlow, Hazard, CCP, CCPMonitoringLog, CCPVerificationLog,
    HazardType, RiskLevel, CCPStatus,
    HACCPPlan, HACCPPlanVersion, HACCPPlanApproval, HACCPPlanStatus,
    ProductRiskConfig, DecisionTree
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

logger = logging.getLogger(__name__)


class HACCPService:
    """
    Service for handling HACCP business logic
    """
    
    def __init__(self, db: Session):
        self.db = db

    def user_has_required_training(self, user_id: int, action: str, *, ccp_id: int | None = None, equipment_id: int | None = None) -> bool:
        """
        Check if a user meets competency (training) requirements for a given HACCP action.
        Action can be "monitor" or "verify". Uses RoleRequiredTraining as configuration:
        - If the user's role has mandatory trainings defined, require completion (attendance or certificate)
          for all those programs.
        - If no role requirements exist, return True (no configured requirements).
        """
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
                    TrainingAttendance.attended == True,
                )
                .distinct()
                .all()
        }

        # Certificate-based completion
        certified_program_ids = {
            pid for (pid,) in self.db.query(TrainingSession.program_id)
                .join(TrainingCertificate, TrainingCertificate.session_id == TrainingSession.id)
                .filter(TrainingCertificate.user_id == user_id)
                .distinct()
                .all()
        }

        completed_program_ids = attended_program_ids.union(certified_program_ids)

        # Require all mandatory programs to be completed
        missing = required_program_ids.difference(completed_program_ids)
        return len(missing) == 0
    
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
            references=hazard_data.references,  # New field for reference documents
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
        control_threshold = threshold.medium_threshold if threshold else 8
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
            created_by=created_by
        )
        
        self.db.add(monitoring_log)
        self.db.commit()
        self.db.refresh(monitoring_log)
        
        # Create alert if out of spec and auto-create Non-Conformance
        alert_created = False
        if not is_within_limits:
            alert_created = self._create_out_of_spec_alert(ccp, monitoring_log)

            # Attempt to create a Non-Conformance when out-of-spec
            try:
                from app.schemas.nonconformance import (
                    NonConformanceCreate as NCCreate,
                    NonConformanceSource,
                )
                from app.services.nonconformance_service import NonConformanceService

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
                nc_service.create_non_conformance(nc_data, reporter)
            except Exception as _:
                # Do not break monitoring log creation if NC creation fails
                pass

        return monitoring_log, alert_created
    
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